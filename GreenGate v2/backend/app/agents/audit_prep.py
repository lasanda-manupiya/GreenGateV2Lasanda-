from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base_agent import BaseAgent
from app.models.audit import AuditEntry, CrpDocument, SecurityCheck
from app.models.emissions import EmissionsInventory
from app.models.organisation import Organisation
from app.models.submission import Submission
from app.services.evidence_service import generate_evidence_pack

logger = logging.getLogger("sustaingate.agent.audit_prep")


class AuditPrep(BaseAgent):
    """Gate 4 agent: Prepares audit evidence packs and pre-audit checks.

    Core responsibilities:
      - Generate evidence packs (ZIP of CSVs + CRP + manifest)
      - Run deterministic readiness checks before external audit
      - Produce AI-generated pre-audit risk assessment
    """

    def __init__(self, agent_record, governance_engine, claude_client, db: AsyncSession):
        super().__init__(agent_record, governance_engine, claude_client, db)

    async def _execute(self, org_id: uuid.UUID, action: str, payload: dict) -> dict:
        if action == "generate_evidence_pack":
            return await self._generate_evidence_pack(org_id, payload)
        elif action == "run_readiness_check":
            return await self._run_readiness_check(org_id, payload)
        elif action == "pre_audit_review":
            return await self._pre_audit_review(org_id, payload)
        else:
            raise ValueError(f"Unsupported action: {action}")

    async def _generate_evidence_pack(self, org_id: uuid.UUID, payload: dict) -> dict:
        """Delegate to the existing evidence_service utility."""
        zip_path = await generate_evidence_pack(self.db, org_id)
        size_bytes = zip_path.stat().st_size if zip_path.exists() else 0

        return {
            "status": "ok",
            "evidence_pack_path": str(zip_path),
            "filename": zip_path.name,
            "size_bytes": size_bytes,
            "size_kb": round(size_bytes / 1024, 2),
            "contents": [
                "emissions_inventory.csv",
                "audit_trail.csv",
                "submissions.csv",
                "security_checks.csv",
                "MANIFEST.txt",
            ],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    async def _run_readiness_check(self, org_id: uuid.UUID, payload: dict) -> dict:
        """Deterministic pre-audit checklist. No Claude involvement."""
        checks: list[dict] = []

        # Check 1: Emissions inventory populated
        em_result = await self.db.execute(
            select(func.count(EmissionsInventory.id)).where(
                EmissionsInventory.organisation_id == str(org_id)
            )
        )
        emissions_count = em_result.scalar() or 0
        checks.append(
            {
                "id": "emissions_inventory",
                "description": "Emissions inventory has at least one row",
                "status": "pass" if emissions_count > 0 else "fail",
                "detail": f"{emissions_count} inventory rows",
            }
        )

        # Check 2: CRP exists and is approved
        crp_result = await self.db.execute(
            select(CrpDocument).where(CrpDocument.organisation_id == str(org_id))
        )
        crps = list(crp_result.scalars().all())
        approved_crps = [c for c in crps if (c.status or "") in ("final", "approved")]
        if not crps:
            crp_status, crp_detail = "fail", "No Carbon Reduction Plan generated"
        elif not approved_crps:
            crp_status, crp_detail = (
                "warn",
                f"{len(crps)} CRP(s) in draft — none finalised",
            )
        else:
            crp_status, crp_detail = "pass", f"{len(approved_crps)} approved CRP(s)"
        checks.append(
            {
                "id": "crp_approved",
                "description": "At least one approved Carbon Reduction Plan",
                "status": crp_status,
                "detail": crp_detail,
            }
        )

        # Check 3: Audit trail entries exist
        audit_result = await self.db.execute(
            select(func.count(AuditEntry.id)).where(
                AuditEntry.organisation_id == str(org_id)
            )
        )
        audit_count = audit_result.scalar() or 0
        checks.append(
            {
                "id": "audit_trail",
                "description": "Audit trail has entries",
                "status": "pass" if audit_count > 0 else "warn",
                "detail": f"{audit_count} audit entries",
            }
        )

        # Check 4: Security checks completed
        sec_result = await self.db.execute(
            select(
                SecurityCheck.status,
                func.count(SecurityCheck.id),
            )
            .where(SecurityCheck.organisation_id == str(org_id))
            .group_by(SecurityCheck.status)
        )
        sec_by_status = {s: int(c) for s, c in sec_result.all()}
        total_sec = sum(sec_by_status.values())
        pass_count = sec_by_status.get("pass", 0)
        if total_sec == 0:
            sec_status, sec_detail = "warn", "No security checks run"
        elif pass_count / total_sec >= 0.8:
            sec_status, sec_detail = (
                "pass",
                f"{pass_count}/{total_sec} security checks passed",
            )
        else:
            sec_status, sec_detail = (
                "warn",
                f"Only {pass_count}/{total_sec} security checks passed",
            )
        checks.append(
            {
                "id": "security_checks",
                "description": "Security checks ≥80% pass rate",
                "status": sec_status,
                "detail": sec_detail,
            }
        )

        # Check 5: Submissions history
        sub_result = await self.db.execute(
            select(func.count(Submission.id)).where(
                Submission.organisation_id == str(org_id)
            )
        )
        submissions_count = sub_result.scalar() or 0
        checks.append(
            {
                "id": "submissions",
                "description": "At least one framework submission on record",
                "status": "pass" if submissions_count > 0 else "warn",
                "detail": f"{submissions_count} submission(s)",
            }
        )

        # Overall readiness
        fail_count = sum(1 for c in checks if c["status"] == "fail")
        warn_count = sum(1 for c in checks if c["status"] == "warn")
        pass_count = sum(1 for c in checks if c["status"] == "pass")

        if fail_count > 0:
            overall = "not_ready"
        elif warn_count > 1:
            overall = "needs_attention"
        else:
            overall = "ready"

        return {
            "overall_status": overall,
            "summary": {
                "passed": pass_count,
                "warnings": warn_count,
                "failures": fail_count,
                "total": len(checks),
            },
            "checks": checks,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    async def _pre_audit_review(self, org_id: uuid.UUID, payload: dict) -> dict:
        """Narrative risk assessment using Claude, grounded in real data."""
        readiness = await self._run_readiness_check(org_id, payload)

        org_result = await self.db.execute(
            select(Organisation).where(Organisation.id == str(org_id))
        )
        org = org_result.scalar_one_or_none()
        org_name = org.name if org else "Organisation"
        org_sector = org.sector if org and org.sector else "General"

        # Pull latest CRP summary for context
        crp_result = await self.db.execute(
            select(CrpDocument)
            .where(CrpDocument.organisation_id == str(org_id))
            .order_by(CrpDocument.created_at.desc())
        )
        latest_crp = crp_result.scalars().first()
        crp_summary = "No CRP available"
        if latest_crp and latest_crp.content:
            crp_summary = json.dumps(latest_crp.content, indent=2)[:1500]

        prompt = (
            f"Organisation: {org_name} (sector: {org_sector})\n\n"
            f"Readiness check results:\n{json.dumps(readiness, indent=2)}\n\n"
            f"Latest CRP extract:\n{crp_summary}\n\n"
            f"Based ONLY on the data above, identify the top 5 areas most "
            f"likely to receive auditor questions or challenges. For each, "
            f"cite which specific record or check it refers to. Return JSON "
            f"with a 'risk_areas' array: area, related_check_id, likelihood, "
            f"suggested_preparation. Do not invent data not present above."
        )

        constraints = self._get_constraints()
        response = await self.claude.complete(
            system_prompt=(
                "You are a pre-audit reviewer for UK sustainability "
                "compliance. Only cite facts present in the provided "
                "readiness data and CRP extract. Never fabricate evidence."
            ),
            user_message=prompt,
            policy_constraints=constraints,
        )

        try:
            risk_analysis = json.loads(response)
        except json.JSONDecodeError:
            risk_analysis = {"raw_response": response}

        return {
            "readiness": readiness,
            "risk_analysis": risk_analysis,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
