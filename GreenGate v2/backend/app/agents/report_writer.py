from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base_agent import BaseAgent
from app.models.audit import CrpDocument
from app.models.emissions import EmissionsInventory
from app.models.framework import Framework
from app.models.organisation import Organisation
from app.models.submission import Submission

logger = logging.getLogger("sustaingate.agent.report_writer")


class ReportWriter(BaseAgent):
    """Gate 5 agent: Generates framework-specific compliance reports.

    Core responsibilities:
      - List available reports based on org's enrolled frameworks
      - Compile disclosure data deterministically from DB
      - Generate AI-assisted framework-specific reports and persist as Submission drafts
    """

    def __init__(self, agent_record, governance_engine, claude_client, db: AsyncSession):
        super().__init__(agent_record, governance_engine, claude_client, db)

    async def _execute(self, org_id: uuid.UUID, action: str, payload: dict) -> dict:
        if action == "list_available_reports":
            return await self._list_available_reports(org_id, payload)
        elif action == "compile_disclosure":
            return await self._compile_disclosure(org_id, payload)
        elif action == "generate_report":
            return await self._generate_report(org_id, payload)
        else:
            raise ValueError(f"Unsupported action: {action}")

    async def _list_available_reports(self, org_id: uuid.UUID, payload: dict) -> dict:
        """List frameworks the org can generate reports for."""
        org_result = await self.db.execute(
            select(Organisation).where(Organisation.id == str(org_id))
        )
        org = org_result.scalar_one_or_none()
        if not org:
            return {"error": "Organisation not found"}

        enrolled = org.frameworks_enrolled or []

        fw_result = await self.db.execute(
            select(Framework).where(Framework.is_active.is_(True))
        )
        frameworks = list(fw_result.scalars().all())

        available = []
        for fw in frameworks:
            is_enrolled = any(
                (isinstance(e, dict) and e.get("name") == fw.name)
                or (isinstance(e, str) and e == fw.name)
                for e in enrolled
            )
            available.append(
                {
                    "framework_id": str(fw.id),
                    "name": fw.name,
                    "version": fw.version,
                    "jurisdiction": fw.jurisdiction,
                    "gate_number": fw.gate_number,
                    "enrolled": is_enrolled,
                    "description": fw.description,
                }
            )

        return {
            "organisation": org.name,
            "frameworks_enrolled_count": len(enrolled),
            "available_reports": available,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    async def _compile_disclosure(self, org_id: uuid.UUID, payload: dict) -> dict:
        """Deterministically compile the disclosure dataset for a framework.

        No Claude call — this is the factual payload that feeds generate_report.
        """
        # Org
        org_result = await self.db.execute(
            select(Organisation).where(Organisation.id == str(org_id))
        )
        org = org_result.scalar_one_or_none()
        if not org:
            return {"error": "Organisation not found"}

        # Emissions by scope
        scope_query = (
            select(EmissionsInventory.scope, func.sum(EmissionsInventory.co2e_tonnes))
            .where(EmissionsInventory.organisation_id == str(org_id))
            .group_by(EmissionsInventory.scope)
        )
        scope_result = await self.db.execute(scope_query)
        scope_totals = {int(s): float(t or 0) for s, t in scope_result.all()}

        # Latest CRP
        crp_result = await self.db.execute(
            select(CrpDocument)
            .where(CrpDocument.organisation_id == str(org_id))
            .order_by(CrpDocument.created_at.desc())
        )
        latest_crp = crp_result.scalars().first()

        # Confidence breakdown
        confidence_query = (
            select(
                EmissionsInventory.confidence_tier,
                func.count(EmissionsInventory.id),
            )
            .where(EmissionsInventory.organisation_id == str(org_id))
            .group_by(EmissionsInventory.confidence_tier)
        )
        confidence_result = await self.db.execute(confidence_query)
        confidence_breakdown = {
            (tier or "unknown"): int(count) for tier, count in confidence_result.all()
        }

        return {
            "organisation": {
                "name": org.name,
                "sector": org.sector,
                "employee_count": org.employee_count,
                "turnover_band": org.turnover_band,
                "country": org.country,
                "company_number": org.company_number,
            },
            "emissions": {
                "scope1_tco2e": round(scope_totals.get(1, 0.0), 2),
                "scope2_tco2e": round(scope_totals.get(2, 0.0), 2),
                "scope3_tco2e": round(scope_totals.get(3, 0.0), 2),
                "total_tco2e": round(sum(scope_totals.values()), 2),
            },
            "data_quality": {
                "confidence_breakdown": confidence_breakdown,
            },
            "crp": {
                "available": latest_crp is not None,
                "version": latest_crp.version if latest_crp else None,
                "status": latest_crp.status if latest_crp else None,
                "ppn006_aligned": latest_crp.ppn006_aligned if latest_crp else None,
                "sbti_target": latest_crp.sbti_target if latest_crp else None,
            },
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    async def _generate_report(self, org_id: uuid.UUID, payload: dict) -> dict:
        """Generate a framework-specific report via Claude and persist as draft Submission."""
        framework_id = payload.get("framework_id")
        if not framework_id:
            return {"error": "framework_id is required in payload"}

        fw_result = await self.db.execute(
            select(Framework).where(Framework.id == str(framework_id))
        )
        framework = fw_result.scalar_one_or_none()
        if not framework:
            return {"error": f"Framework {framework_id} not found"}

        # Gather disclosure payload (deterministic)
        disclosure = await self._compile_disclosure(org_id, payload)
        if disclosure.get("error"):
            return disclosure

        prompt = (
            f"Generate a compliance report for the following framework.\n\n"
            f"Framework: {framework.name} (version: {framework.version or 'current'})\n"
            f"Jurisdiction: {framework.jurisdiction or 'UK'}\n"
            f"Description: {framework.description or ''}\n\n"
            f"Organisation disclosure data:\n"
            f"{json.dumps(disclosure, indent=2)}\n\n"
            f"Produce a structured report matching {framework.name}'s required "
            f"sections. Return JSON with: framework, reporting_period, sections "
            f"(object where each key is a section name), and a summary field. "
            f"Cite data from the disclosure payload — do not invent numbers. "
            f"If a required section cannot be populated from the data, mark it "
            f"as 'data_required' with a note describing what is missing."
        )

        constraints = self._get_constraints()
        response = await self.claude.complete(
            system_prompt=(
                f"You are a UK compliance report writer specialising in "
                f"{framework.name}. Every number you write must be traceable "
                f"to the disclosure payload provided. Never fabricate figures."
            ),
            user_message=prompt,
            policy_constraints=constraints,
        )

        try:
            report_content = json.loads(response)
        except json.JSONDecodeError:
            report_content = {
                "raw_content": response,
                "parse_note": "AI response was not valid JSON. Manual review required.",
            }

        # Persist as a draft submission
        submission = Submission(
            organisation_id=str(org_id),
            gate_number=framework.gate_number or 5,
            framework_id=str(framework.id),
            status="draft",
            content={
                "report": report_content,
                "source_disclosure": disclosure,
                "generated_by_agent": str(self.record.id),
            },
        )
        self.db.add(submission)
        await self.db.flush()

        return {
            "submission_id": str(submission.id),
            "framework": framework.name,
            "status": "draft",
            "report": report_content,
            "disclosure_snapshot": disclosure,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
