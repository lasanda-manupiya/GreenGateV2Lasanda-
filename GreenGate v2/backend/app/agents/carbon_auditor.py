from __future__ import annotations

import json
import logging
import uuid
from decimal import Decimal
from typing import Dict, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base_agent import BaseAgent, AgentResult
from app.integrations.defra_factors import DEFRAFactorsService
from app.integrations.xero_stub import get_xero_transactions
from app.integrations.sage_stub import get_sage_transactions
from app.models.emissions import EmissionsInventory

logger = logging.getLogger("sustaingate.agent.carbon_auditor")

# GHG Protocol category mapping
GHG_CATEGORY_MAP = {
    "electricity": {"scope": 2, "ghg_category": "Purchased electricity", "defra_key": "electricity_uk_grid"},
    "gas": {"scope": 1, "ghg_category": "Natural gas combustion", "defra_key": "natural_gas"},
    "natural_gas": {"scope": 1, "ghg_category": "Natural gas combustion", "defra_key": "natural_gas"},
    "diesel": {"scope": 1, "ghg_category": "Mobile combustion - diesel", "defra_key": "diesel"},
    "petrol": {"scope": 1, "ghg_category": "Mobile combustion - petrol", "defra_key": "petrol"},
    "vehicle_fuel": {"scope": 1, "ghg_category": "Mobile combustion", "defra_key": "diesel"},
    "rail_travel": {"scope": 3, "ghg_category": "Business travel - rail", "defra_key": "rail_travel"},
    "domestic_flights": {"scope": 3, "ghg_category": "Business travel - domestic flights", "defra_key": "domestic_flights"},
    "short_haul_flights": {"scope": 3, "ghg_category": "Business travel - short-haul flights", "defra_key": "short_haul_flights"},
    "courier": {"scope": 3, "ghg_category": "Upstream transportation", "defra_key": "freight_road"},
    "logistics": {"scope": 3, "ghg_category": "Upstream transportation", "defra_key": "freight_road"},
    "office_supplies": {"scope": 3, "ghg_category": "Purchased goods", "defra_key": "business_services_spend"},
    "professional_services": {"scope": 3, "ghg_category": "Purchased services", "defra_key": "business_services_spend"},
    "it_equipment": {"scope": 3, "ghg_category": "Capital goods - IT", "defra_key": "it_equipment_spend"},
    "water": {"scope": 3, "ghg_category": "Water supply", "defra_key": "water_supply"},
    "waste": {"scope": 3, "ghg_category": "Waste generated in operations", "defra_key": "general_waste_landfill"},
    "paper": {"scope": 3, "ghg_category": "Purchased goods - paper", "defra_key": "paper"},
}


def categorise_transaction(txn: dict) -> Optional[str]:
    """Map a transaction to a GHG category key based on description and category.

    Standalone function so it can be reused by CSV upload service and other importers.
    """
    desc = (txn.get("description", "") + " " + txn.get("category", "")).lower()

    if any(w in desc for w in ["electric", "power", "grid"]):
        return "electricity"
    elif any(w in desc for w in ["gas", "british gas", "heating"]) and "petrol" not in desc:
        return "natural_gas"
    elif "diesel" in desc:
        return "diesel"
    elif "petrol" in desc or "unleaded" in desc:
        return "petrol"
    elif any(w in desc for w in ["fuel", "shell", "bp ", "esso"]):
        return "vehicle_fuel"
    elif any(w in desc for w in ["rail", "train", "trainline", "national rail"]):
        return "rail_travel"
    elif any(w in desc for w in ["flight", "airline", "easyjet", "british airways"]) and "short" in desc:
        return "short_haul_flights"
    elif any(w in desc for w in ["flight", "airline", "domestic"]):
        return "domestic_flights"
    elif any(w in desc for w in ["courier", "dhl", "fedex", "ups", "parcel"]):
        return "courier"
    elif any(w in desc for w in ["logistics", "haulage", "freight"]):
        return "logistics"
    elif any(w in desc for w in ["office supplies", "stationery", "paper", "printer"]):
        return "paper" if "paper" in desc else "office_supplies"
    elif any(w in desc for w in ["consulting", "professional", "legal", "accounting"]):
        return "professional_services"
    elif any(w in desc for w in ["computer", "laptop", "server", "it equipment"]):
        return "it_equipment"
    elif "water" in desc:
        return "water"
    elif "waste" in desc or "skip" in desc or "disposal" in desc:
        return "waste"
    return None


class CarbonAuditor(BaseAgent):
    """Gate 1 agent: Carbon baseline calculation and emissions inventory."""

    def __init__(self, agent_record, governance_engine, claude_client, db: AsyncSession):
        super().__init__(agent_record, governance_engine, claude_client, db)
        self.defra = DEFRAFactorsService()

    async def _execute(self, org_id: uuid.UUID, action: str, payload: dict) -> dict:
        if action == "scan_invoices":
            return await self._scan_invoices(org_id, payload)
        elif action == "build_inventory":
            return await self._build_inventory(org_id, payload)
        elif action == "calculate_baseline":
            return await self._calculate_baseline(org_id, payload)
        elif action == "assign_confidence":
            return await self._assign_confidence(org_id, payload)
        else:
            raise ValueError(f"Unsupported action: {action}")

    async def _scan_invoices(self, org_id: uuid.UUID, payload: dict) -> dict:
        """Scan invoices from accounting integrations and categorise by GHG category."""
        source = payload.get("source", "xero")
        if source == "sage":
            transactions = get_sage_transactions()
        else:
            transactions = get_xero_transactions()

        categorised = []
        uncategorised = []

        for txn in transactions:
            category_key = categorise_transaction(txn)
            if category_key and category_key in GHG_CATEGORY_MAP:
                mapping = GHG_CATEGORY_MAP[category_key]
                categorised.append({
                    "date": txn["date"],
                    "description": txn["description"],
                    "amount": txn["amount"],
                    "account_category": txn.get("category", ""),
                    "ghg_scope": mapping["scope"],
                    "ghg_category": mapping["ghg_category"],
                    "defra_key": mapping["defra_key"],
                    "supplier": txn.get("supplier_name", "Unknown"),
                })
            else:
                uncategorised.append({
                    "date": txn["date"],
                    "description": txn["description"],
                    "amount": txn["amount"],
                    "category": txn.get("category", "unknown"),
                })

        return {
            "source": source,
            "total_transactions": len(transactions),
            "categorised_count": len(categorised),
            "uncategorised_count": len(uncategorised),
            "categorised_transactions": categorised,
            "uncategorised_transactions": uncategorised,
        }

    async def _build_inventory(self, org_id: uuid.UUID, payload: dict) -> dict:
        """Build a full emissions inventory from categorised transactions using DEFRA factors."""
        reporting_year = payload.get("reporting_year", 2025)

        # First scan invoices to get categorised data
        scan_result = await self._scan_invoices(org_id, payload)
        transactions = scan_result["categorised_transactions"]

        # Aggregate by GHG category
        aggregated: Dict[str, dict] = {}
        for txn in transactions:
            key = txn["ghg_category"]
            if key not in aggregated:
                aggregated[key] = {
                    "scope": txn["ghg_scope"],
                    "category": key,
                    "defra_key": txn["defra_key"],
                    "total_amount": Decimal("0"),
                    "transaction_count": 0,
                }
            aggregated[key]["total_amount"] += Decimal(str(txn["amount"]))
            aggregated[key]["transaction_count"] += 1

        # Apply DEFRA emission factors
        inventory_entries = []
        for key, agg in aggregated.items():
            factor_data = self.defra.get_factor_by_key(agg["defra_key"])
            if not factor_data:
                logger.warning("No DEFRA factor found for key: %s", agg["defra_key"])
                continue

            factor_value = Decimal(str(factor_data["factor_value"]))
            activity_data = agg["total_amount"]

            # Calculate CO2e in tonnes (factors are in kg, so divide by 1000)
            co2e_kg = activity_data * factor_value
            co2e_tonnes = co2e_kg / Decimal("1000")

            entry = EmissionsInventory(
                organisation_id=str(org_id),
                reporting_year=reporting_year,
                scope=agg["scope"],
                category=agg["category"],
                source=f"Accounting integration ({payload.get('source', 'xero')})",
                activity_data=activity_data,
                activity_unit=factor_data["unit"],
                emission_factor=factor_value,
                emission_factor_source=f"DEFRA/DESNZ {factor_data['year']}",
                co2e_tonnes=round(co2e_tonnes, 6),
                confidence_tier="medium",
                data_source="accounting_integration",
                notes=f"Auto-calculated from {agg['transaction_count']} transactions",
            )
            self.db.add(entry)
            inventory_entries.append({
                "scope": agg["scope"],
                "category": agg["category"],
                "activity_data": float(activity_data),
                "activity_unit": factor_data["unit"],
                "emission_factor": float(factor_value),
                "co2e_tonnes": float(round(co2e_tonnes, 6)),
                "transaction_count": agg["transaction_count"],
            })

        await self.db.flush()

        return {
            "reporting_year": reporting_year,
            "entries_created": len(inventory_entries),
            "inventory": inventory_entries,
            "total_co2e_tonnes": sum(e["co2e_tonnes"] for e in inventory_entries),
        }

    async def _calculate_baseline(self, org_id: uuid.UUID, payload: dict) -> dict:
        """Aggregate inventory into scope-level baseline totals."""
        reporting_year = payload.get("reporting_year")

        # Query existing inventory
        query = select(
            EmissionsInventory.scope,
            func.sum(EmissionsInventory.co2e_tonnes),
            func.count(EmissionsInventory.id),
        ).where(
            EmissionsInventory.organisation_id == str(org_id)
        ).group_by(EmissionsInventory.scope)

        if reporting_year:
            query = query.where(EmissionsInventory.reporting_year == reporting_year)

        result = await self.db.execute(query)
        scope_data = result.all()

        if not scope_data:
            return {"error": "No emissions data found. Run build_inventory first."}

        baseline = {}
        total = Decimal("0")
        for scope, total_co2e, count in scope_data:
            scope_key = f"scope{scope}"
            amount = total_co2e or Decimal("0")
            baseline[scope_key] = {
                "total_co2e_tonnes": float(amount),
                "entry_count": count,
            }
            total += amount

        baseline["total_co2e_tonnes"] = float(total)

        # SBTi 1.5C target: 4.2% annual linear reduction
        baseline["sbti_target"] = {
            "pathway": "1.5C",
            "annual_reduction_rate": 0.042,
            "2030_target_tonnes": float(total * Decimal("0.79")),  # ~21% reduction over 5 years
        }

        return baseline

    async def _assign_confidence(self, org_id: uuid.UUID, payload: dict) -> dict:
        """Use Claude to assess data quality and assign confidence tiers."""
        # Fetch inventory
        result = await self.db.execute(
            select(EmissionsInventory)
            .where(EmissionsInventory.organisation_id == str(org_id))
            .order_by(EmissionsInventory.scope, EmissionsInventory.category)
        )
        entries = list(result.scalars().all())

        if not entries:
            return {"error": "No emissions data found. Run build_inventory first."}

        # Build summary for Claude
        summary_lines = []
        for e in entries:
            summary_lines.append(
                f"- Scope {e.scope}, {e.category}: {e.co2e_tonnes} tCO2e, "
                f"source='{e.data_source}', factor_source='{e.emission_factor_source}'"
            )
        summary_text = "\n".join(summary_lines)

        prompt = (
            f"Assess the data quality of the following emissions inventory entries "
            f"and assign confidence tiers (high/medium/low/estimated) to each.\n\n"
            f"Inventory:\n{summary_text}\n\n"
            f"For each entry, provide the category name, recommended tier, and reason. "
            f"Also provide overall data quality assessment and recommendations for improvement."
        )

        constraints = self._get_constraints()
        response = await self.claude.complete(
            system_prompt=(
                "You are a GHG Protocol data quality assessor. "
                "Assign confidence tiers based on data source quality, "
                "completeness, and methodology."
            ),
            user_message=prompt,
            policy_constraints=constraints,
        )

        # Parse and apply confidence tiers from response
        # For MVP, try JSON parse; fall back to simple assignment
        try:
            parsed = json.loads(response)
            assessments = parsed.get("assessment", [])
            for assessment in assessments:
                cat_name = assessment.get("category", "")
                tier = assessment.get("tier", "medium")
                for entry in entries:
                    if cat_name.lower() in entry.category.lower():
                        entry.confidence_tier = tier
            await self.db.flush()
        except (json.JSONDecodeError, KeyError):
            logger.info("Could not parse Claude response as JSON, using response as-is")

        return {
            "entries_assessed": len(entries),
            "ai_assessment": response,
        }
