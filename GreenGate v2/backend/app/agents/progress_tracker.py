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
from app.models.organisation import Organisation

logger = logging.getLogger("sustaingate.agent.progress_tracker")


class ProgressTracker(BaseAgent):
    """Gate 3 agent: Monitors emissions trends against reduction targets.

    Core responsibilities:
      - Compare current emissions against SBTi target trajectory
      - Forecast future emissions based on historical rate of change
      - Flag deviations from the net-zero pathway and generate recommendations
    """

    DEFAULT_DEVIATION_THRESHOLD_PCT = 10.0

    def __init__(self, agent_record, governance_engine, claude_client, db: AsyncSession):
        super().__init__(agent_record, governance_engine, claude_client, db)

    async def _execute(self, org_id: uuid.UUID, action: str, payload: dict) -> dict:
        if action == "track_progress":
            return await self._track_progress(org_id, payload)
        elif action == "forecast_trajectory":
            return await self._forecast_trajectory(org_id, payload)
        elif action == "flag_deviations":
            return await self._flag_deviations(org_id, payload)
        else:
            raise ValueError(f"Unsupported action: {action}")

    async def _get_latest_sbti_target(self, org_id: uuid.UUID) -> dict | None:
        """Fetch the SBTi target from the most recent CRP document."""
        result = await self.db.execute(
            select(CrpDocument)
            .where(CrpDocument.organisation_id == str(org_id))
            .order_by(CrpDocument.created_at.desc())
        )
        crp = result.scalars().first()
        if crp and crp.sbti_target:
            return crp.sbti_target
        return None

    async def _get_emissions_by_year(self, org_id: uuid.UUID) -> dict[int, dict]:
        """Aggregate emissions by reporting year and scope."""
        query = (
            select(
                EmissionsInventory.reporting_year,
                EmissionsInventory.scope,
                func.sum(EmissionsInventory.co2e_tonnes),
            )
            .where(EmissionsInventory.organisation_id == str(org_id))
            .group_by(EmissionsInventory.reporting_year, EmissionsInventory.scope)
            .order_by(EmissionsInventory.reporting_year)
        )
        result = await self.db.execute(query)

        by_year: dict[int, dict] = {}
        for year, scope, total in result.all():
            if year is None:
                continue
            bucket = by_year.setdefault(
                year,
                {"scope1": 0.0, "scope2": 0.0, "scope3": 0.0, "total": 0.0},
            )
            val = float(total or 0)
            bucket[f"scope{scope}"] = val
            bucket["total"] += val
        return by_year

    async def _track_progress(self, org_id: uuid.UUID, payload: dict) -> dict:
        """Compare current emissions vs. SBTi target trajectory."""
        sbti = await self._get_latest_sbti_target(org_id)
        if not sbti:
            return {
                "status": "warn",
                "error": "No SBTi target found. Generate a CRP first (Gate 2).",
            }

        emissions_by_year = await self._get_emissions_by_year(org_id)
        if not emissions_by_year:
            return {
                "status": "warn",
                "error": "No emissions data found. Run Carbon Auditor first (Gate 1).",
            }

        latest_year = max(emissions_by_year.keys())
        latest = emissions_by_year[latest_year]
        year_by_year = sbti.get("year_by_year") or {}
        target_for_year = year_by_year.get(str(latest_year))

        if target_for_year is None:
            # Compute inline if not stored explicitly
            base_emissions = float(sbti.get("base_emissions_tco2e") or 0)
            base_year = int(sbti.get("base_year") or latest_year)
            annual_pct = float(sbti.get("annual_reduction_pct") or 4.2) / 100.0
            years_elapsed = max(0, latest_year - base_year)
            target_for_year = max(0.0, base_emissions - (base_emissions * annual_pct * years_elapsed))

        actual = latest["total"]
        variance = actual - float(target_for_year)
        variance_pct = (variance / float(target_for_year) * 100.0) if target_for_year else 0.0

        if variance_pct <= 0:
            track_status = "on_track"
        elif variance_pct <= self.DEFAULT_DEVIATION_THRESHOLD_PCT:
            track_status = "at_risk"
        else:
            track_status = "off_track"

        return {
            "status": track_status,
            "reporting_year": latest_year,
            "actual_tco2e": round(actual, 2),
            "target_tco2e": round(float(target_for_year), 2),
            "variance_tco2e": round(variance, 2),
            "variance_pct": round(variance_pct, 2),
            "scope_breakdown": {
                "scope1": round(latest["scope1"], 2),
                "scope2": round(latest["scope2"], 2),
                "scope3": round(latest["scope3"], 2),
            },
            "sbti_pathway": sbti.get("pathway", "1.5C"),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    async def _forecast_trajectory(self, org_id: uuid.UUID, payload: dict) -> dict:
        """Project emissions forward based on historical rate of change."""
        emissions_by_year = await self._get_emissions_by_year(org_id)
        if len(emissions_by_year) < 2:
            return {
                "error": "Need at least 2 years of emissions data to forecast",
                "years_available": list(emissions_by_year.keys()),
            }

        years = sorted(emissions_by_year.keys())
        first_total = emissions_by_year[years[0]]["total"]
        last_total = emissions_by_year[years[-1]]["total"]
        year_span = years[-1] - years[0]

        if year_span == 0 or first_total == 0:
            annual_change_pct = 0.0
        else:
            # Compound annual growth rate
            annual_change_pct = (((last_total / first_total) ** (1 / year_span)) - 1) * 100.0

        # Project forward to 2030, 2040, 2050
        projections: dict[str, float] = {}
        for target_year in (2030, 2035, 2040, 2050):
            years_out = target_year - years[-1]
            if years_out <= 0:
                projections[str(target_year)] = round(last_total, 2)
                continue
            projected = last_total * ((1 + annual_change_pct / 100.0) ** years_out)
            projections[str(target_year)] = round(max(0.0, projected), 2)

        # Compare against SBTi if available
        sbti = await self._get_latest_sbti_target(org_id)
        sbti_gap = None
        if sbti:
            sbti_2030 = float(sbti.get("target_2030") or 0)
            sbti_gap = {
                "sbti_target_2030": round(sbti_2030, 2),
                "projected_2030": projections["2030"],
                "gap_2030": round(projections["2030"] - sbti_2030, 2),
            }

        return {
            "historical": {str(y): round(emissions_by_year[y]["total"], 2) for y in years},
            "annual_change_pct": round(annual_change_pct, 2),
            "projections": projections,
            "sbti_comparison": sbti_gap,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    async def _flag_deviations(self, org_id: uuid.UUID, payload: dict) -> dict:
        """Identify off-track scopes and generate Claude recommendations."""
        threshold = float(
            payload.get("threshold_pct", self.DEFAULT_DEVIATION_THRESHOLD_PCT)
        )
        progress = await self._track_progress(org_id, payload)

        if progress.get("error"):
            return progress

        deviations: list[dict] = []
        target = progress["target_tco2e"]
        actual = progress["actual_tco2e"]
        if target > 0 and ((actual - target) / target * 100.0) > threshold:
            deviations.append(
                {
                    "metric": "total_emissions",
                    "actual": actual,
                    "target": target,
                    "variance_pct": progress["variance_pct"],
                    "severity": "high" if progress["variance_pct"] > 25 else "medium",
                }
            )

        if not deviations:
            return {
                "status": "on_track",
                "deviations": [],
                "recommendations": [],
                "message": "Emissions are tracking within tolerance of SBTi pathway.",
            }

        # Fetch org for context
        org_result = await self.db.execute(
            select(Organisation).where(Organisation.id == str(org_id))
        )
        org = org_result.scalar_one_or_none()
        org_name = org.name if org else "Organisation"
        org_sector = org.sector if org and org.sector else "General"

        prompt = (
            f"Organisation: {org_name} (sector: {org_sector})\n"
            f"Reporting year: {progress['reporting_year']}\n"
            f"Actual emissions: {actual} tCO2e\n"
            f"SBTi target: {target} tCO2e\n"
            f"Variance: +{progress['variance_pct']}% over target\n"
            f"Scope breakdown: {progress['scope_breakdown']}\n\n"
            f"Generate a prioritised list of corrective actions to get this "
            f"organisation back on the 1.5C SBTi pathway. Return JSON with a "
            f"'recommendations' array, each containing: action, scope, "
            f"estimated_reduction_tco2e, timeline_months, priority."
        )

        constraints = self._get_constraints()
        response = await self.claude.complete(
            system_prompt=(
                "You are a net-zero transition advisor. Recommend concrete "
                "corrective actions grounded in the organisation's actual "
                "emissions data. Never fabricate baseline figures."
            ),
            user_message=prompt,
            policy_constraints=constraints,
        )

        try:
            recommendations = json.loads(response)
        except json.JSONDecodeError:
            recommendations = {"raw_response": response}

        return {
            "status": "off_track",
            "deviations": deviations,
            "progress_summary": progress,
            "recommendations": recommendations,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
