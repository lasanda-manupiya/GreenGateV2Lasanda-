from __future__ import annotations

import json
import logging
import uuid
from decimal import Decimal

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base_agent import BaseAgent
from app.models.emissions import EmissionsInventory
from app.models.organisation import Organisation
from app.models.audit import CrpDocument
from app.services.crp_service import create_crp_document

logger = logging.getLogger("sustaingate.agent.strategy_builder")


class StrategyBuilder(BaseAgent):
    """Gate 2 agent: Net-zero strategy and CRP generation."""

    def __init__(self, agent_record, governance_engine, claude_client, db: AsyncSession):
        super().__init__(agent_record, governance_engine, claude_client, db)

    async def _execute(self, org_id: uuid.UUID, action: str, payload: dict) -> dict:
        # Normalize to str for SQLAlchemy String(36) columns (SQLite cannot bind raw UUID).
        org_id = str(org_id)
        if action == "generate_crp":
            return await self._generate_crp(org_id, payload)
        elif action == "calculate_sbti_target":
            return await self._calculate_sbti_target(org_id, payload)
        elif action == "recommend_frameworks":
            return await self._recommend_frameworks(org_id, payload)
        else:
            raise ValueError(f"Unsupported action: {action}")

    async def _generate_crp(self, org_id: uuid.UUID, payload: dict) -> dict:
        """Generate a Carbon Reduction Plan structured per PPN 006 Technical Standard."""
        # Fetch organisation details
        org_result = await self.db.execute(
            select(Organisation).where(Organisation.id == org_id)
        )
        org = org_result.scalar_one_or_none()
        org_name = org.name if org else "Organisation"
        org_sector = org.sector if org else "General"

        # Fetch emissions baseline
        scope_query = select(
            EmissionsInventory.scope,
            func.sum(EmissionsInventory.co2e_tonnes),
        ).where(
            EmissionsInventory.organisation_id == org_id
        ).group_by(EmissionsInventory.scope)

        scope_result = await self.db.execute(scope_query)
        scope_totals = {scope: float(total or 0) for scope, total in scope_result.all()}

        total_emissions = sum(scope_totals.values())
        scope1 = scope_totals.get(1, 0)
        scope2 = scope_totals.get(2, 0)
        scope3 = scope_totals.get(3, 0)

        # Calculate SBTi target
        sbti = self._compute_sbti_target(total_emissions)

        # Build context for Claude
        emissions_context = (
            f"Organisation: {org_name}\n"
            f"Sector: {org_sector}\n"
            f"Baseline Emissions:\n"
            f"  Scope 1: {scope1:.2f} tCO2e\n"
            f"  Scope 2: {scope2:.2f} tCO2e\n"
            f"  Scope 3: {scope3:.2f} tCO2e\n"
            f"  Total: {total_emissions:.2f} tCO2e\n"
            f"SBTi 1.5C Target: {sbti['annual_reduction_pct']}% annual reduction\n"
            f"  2030 Target: {sbti['target_2030']:.2f} tCO2e\n"
        )

        prompt = (
            f"Generate a comprehensive Carbon Reduction Plan (CRP) for the following organisation.\n\n"
            f"{emissions_context}\n\n"
            f"The CRP must:\n"
            f"1. Meet PPN 006 Technical Standard requirements\n"
            f"2. Include commitments to Net Zero by 2050 with interim targets\n"
            f"3. Reference the baseline emissions data above\n"
            f"4. Include specific, measurable reduction measures\n"
            f"5. Include governance arrangements and director sign-off section\n"
            f"6. Align targets with SBTi 1.5C pathway\n\n"
            f"Return the CRP as a structured JSON document with sections: "
            f"commitment, baseline_emissions, current_emissions, reduction_targets, "
            f"reduction_measures, governance, ppn006_declaration, director_sign_off_required."
        )

        constraints = self._get_constraints()
        response = await self.claude.complete(
            system_prompt=(
                "You are a sustainability consultant specialising in UK public sector "
                "Carbon Reduction Plans. Generate CRPs that comply with PPN 006/21 "
                "Technical Standard and align with SBTi Science Based Targets."
            ),
            user_message=prompt,
            policy_constraints=constraints,
        )

        # Parse CRP content
        try:
            crp_content = json.loads(response)
        except json.JSONDecodeError:
            crp_content = {
                "raw_content": response,
                "parse_note": "AI response was not valid JSON. Manual review required.",
            }

        # Save to database
        crp_doc = await create_crp_document(
            self.db,
            organisation_id=org_id,
            content=crp_content,
            agent_id=self.record.id,
            ppn006_aligned=True,
            sbti_target=sbti,
        )

        return {
            "crp_id": str(crp_doc.id),
            "version": crp_doc.version,
            "content": crp_content,
            "sbti_target": sbti,
            "ppn006_aligned": True,
            "baseline": {
                "scope1": scope1,
                "scope2": scope2,
                "scope3": scope3,
                "total": total_emissions,
            },
        }

    async def _calculate_sbti_target(self, org_id: uuid.UUID, payload: dict) -> dict:
        """Deterministic calculation of SBTi 1.5C pathway targets."""
        # Fetch total baseline emissions
        total_result = await self.db.execute(
            select(func.sum(EmissionsInventory.co2e_tonnes)).where(
                EmissionsInventory.organisation_id == org_id
            )
        )
        total_emissions = float(total_result.scalar() or 0)

        if total_emissions == 0:
            return {"error": "No emissions data found. Calculate baseline first."}

        base_year = payload.get("base_year", 2025)
        return self._compute_sbti_target(total_emissions, base_year)

    def _compute_sbti_target(
        self, total_emissions: float, base_year: int = 2025
    ) -> dict:
        """Compute SBTi 1.5C pathway targets (deterministic)."""
        # SBTi 1.5C pathway: ~4.2% annual linear reduction from base year
        annual_reduction_rate = 0.042
        targets = {}
        for year in range(base_year, 2051):
            years_elapsed = year - base_year
            reduction = total_emissions * annual_reduction_rate * years_elapsed
            target = max(0, total_emissions - reduction)
            targets[str(year)] = round(target, 2)

        return {
            "pathway": "1.5C",
            "base_year": base_year,
            "base_emissions_tco2e": round(total_emissions, 2),
            "annual_reduction_pct": 4.2,
            "annual_reduction_tco2e": round(total_emissions * annual_reduction_rate, 2),
            "target_2030": targets.get(str(2030), 0),
            "target_2035": targets.get(str(2035), 0),
            "target_2040": targets.get(str(2040), 0),
            "target_2050": targets.get(str(2050), 0),
            "year_by_year": targets,
            "net_zero_year": 2050,
        }

    async def _recommend_frameworks(self, org_id: uuid.UUID, payload: dict) -> dict:
        """Use Claude to analyse org profile and recommend appropriate frameworks."""
        org_result = await self.db.execute(
            select(Organisation).where(Organisation.id == org_id)
        )
        org = org_result.scalar_one_or_none()
        if not org:
            return {"error": "Organisation not found"}

        profile = (
            f"Organisation: {org.name}\n"
            f"Sector: {org.sector or 'Not specified'}\n"
            f"Employee count: {org.employee_count or 'Not specified'}\n"
            f"Turnover band: {org.turnover_band or 'Not specified'}\n"
            f"Country: {org.country}\n"
            f"Currently enrolled frameworks: {org.frameworks_enrolled or []}\n"
        )

        prompt = (
            f"Based on the following organisation profile, recommend the most "
            f"appropriate sustainability and compliance frameworks, in priority order.\n\n"
            f"{profile}\n\n"
            f"Consider: GHG Protocol, PPN 006, SBTi, CDP, NHS Evergreen, UK SRS, "
            f"EUDR, EPR, ISO 14001, Cyber Essentials, ISO 27001, GDPR.\n\n"
            f"Return as JSON with recommended_frameworks (array with name, priority, reason) "
            f"and recommended_sequence."
        )

        constraints = self._get_constraints()
        response = await self.claude.complete(
            system_prompt=(
                "You are a UK sustainability compliance advisor. Recommend frameworks "
                "based on organisation size, sector, and regulatory obligations."
            ),
            user_message=prompt,
            policy_constraints=constraints,
        )

        try:
            recommendations = json.loads(response)
        except json.JSONDecodeError:
            recommendations = {"raw_response": response}

        return recommendations
