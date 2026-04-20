"""Idempotent seed data for SustainGate MVP."""

from __future__ import annotations

import logging
import uuid
from datetime import date

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.framework import Framework, Rule
from app.models.agent import Agent

logger = logging.getLogger("sustaingate.seed")


async def run_seed(db: AsyncSession) -> None:
    """Run all seed functions. Idempotent: checks before inserting."""
    await seed_frameworks(db)
    await seed_agents(db)
    await db.flush()
    logger.info("Seed data loaded successfully")


# ---------------------------------------------------------------------------
# Frameworks
# ---------------------------------------------------------------------------

FRAMEWORKS = [
    {
        "name": "GHG Protocol Corporate Standard",
        "version": "2024 Rev",
        "description": "The GHG Protocol Corporate Accounting and Reporting Standard provides requirements and guidance for companies preparing a corporate-level GHG emissions inventory.",
        "jurisdiction": "International",
        "gate_number": 1,
    },
    {
        "name": "PPN 006",
        "version": "2021/2024",
        "description": "Procurement Policy Note 006/21 requires suppliers bidding for UK Government contracts to provide a Carbon Reduction Plan.",
        "jurisdiction": "UK",
        "gate_number": 2,
    },
    {
        "name": "NHS Evergreen Sustainable Supplier Assessment",
        "version": "2024",
        "description": "NHS England's assessment framework requiring suppliers to demonstrate net-zero roadmaps aligned with the NHS net zero by 2045 supply chain target.",
        "jurisdiction": "UK",
        "gate_number": 2,
    },
    {
        "name": "Science Based Targets initiative (SBTi)",
        "version": "2.1",
        "description": "Framework for companies to set emissions reduction targets consistent with the Paris Agreement goal of limiting warming to 1.5C.",
        "jurisdiction": "International",
        "gate_number": 2,
    },
    {
        "name": "UK Sustainability Reporting Standards (UK SRS)",
        "version": "Draft 2025",
        "description": "UK-endorsed sustainability disclosure standards based on ISSB S1/S2, for mandatory climate-related financial disclosures.",
        "jurisdiction": "UK",
        "gate_number": 5,
    },
    {
        "name": "CDP Climate Change",
        "version": "2025",
        "description": "Carbon Disclosure Project questionnaire for environmental reporting, scoring and benchmarking.",
        "jurisdiction": "International",
        "gate_number": 5,
    },
    {
        "name": "Extended Producer Responsibility (EPR)",
        "version": "2025",
        "description": "UK packaging EPR scheme requiring obligated producers to fund collection, recycling and disposal of packaging waste.",
        "jurisdiction": "UK",
        "gate_number": 3,
    },
    {
        "name": "EU Deforestation Regulation (EUDR)",
        "version": "2023/1115",
        "description": "EU regulation requiring due diligence to ensure products placed on the EU market are deforestation-free.",
        "jurisdiction": "EU",
        "gate_number": 3,
    },
]

# Rules per framework: (framework_index, code, description, rule_type, severity, check_expression)
RULES = [
    # GHG Protocol (index 0)
    (0, "GHG-001", "Emissions inventory must include all Scope 1 direct emissions", "validation", "blocker",
     {"check_type": "required_fields", "fields": ["scope", "category", "co2e_tonnes"]}),
    (0, "GHG-002", "Scope 2 emissions must use location-based or market-based method", "validation", "blocker",
     {"check_type": "field_present", "field": "emission_factor_source"}),
    (0, "GHG-003", "Emission factors must be from recognised sources (DEFRA, IEA, EPA)", "validation", "warning",
     {"check_type": "data_source_documented"}),
    (0, "GHG-004", "Activity data must have documented units", "validation", "warning",
     {"check_type": "required_fields", "fields": ["activity_data", "activity_unit"]}),
    (0, "GHG-005", "CO2e values must be positive", "threshold", "blocker",
     {"check_type": "numeric_range", "field": "co2e_tonnes", "min": 0}),
    (0, "GHG-006", "Confidence tier must be assigned to each data point", "validation", "warning",
     {"check_type": "confidence_tier"}),
    (0, "GHG-007", "Data gaps exceeding 10% of total must be flagged", "threshold", "warning",
     {"check_type": "threshold", "field": "data_gap_pct", "threshold": 10, "operator": "<="}),

    # PPN 006 (index 1)
    (1, "PPN-001", "CRP must include commitment to Net Zero by 2050", "validation", "blocker",
     {"check_type": "field_present", "field": "commitment"}),
    (1, "PPN-002", "Baseline emissions year must be documented", "validation", "blocker",
     {"check_type": "required_fields", "fields": ["baseline_emissions", "reporting_year"]}),
    (1, "PPN-003", "Current emissions reporting year must be stated", "validation", "blocker",
     {"check_type": "field_present", "field": "current_emissions"}),
    (1, "PPN-004", "Carbon reduction targets must be specified", "validation", "blocker",
     {"check_type": "field_present", "field": "reduction_targets"}),
    (1, "PPN-005", "Environmental management measures must be listed", "validation", "warning",
     {"check_type": "field_present", "field": "reduction_measures"}),
    (1, "PPN-006", "PPN 006 declaration must be included", "validation", "blocker",
     {"check_type": "field_present", "field": "ppn006_declaration"}),

    # NHS Evergreen (index 2)
    (2, "NHS-001", "Net zero roadmap must be aligned with NHS 2045 target", "validation", "blocker",
     {"check_type": "field_present", "field": "net_zero_target"}),
    (2, "NHS-002", "Social value commitments must be documented", "validation", "warning",
     {"check_type": "field_present", "field": "social_value"}),
    (2, "NHS-003", "Supply chain emissions must be included", "validation", "warning",
     {"check_type": "field_present", "field": "scope3_emissions"}),
    (2, "NHS-004", "Sustainable procurement policy required", "validation", "warning",
     {"check_type": "field_present", "field": "procurement_policy"}),
    (2, "NHS-005", "Annual progress reporting commitment", "validation", "blocker",
     {"check_type": "field_present", "field": "progress_reporting"}),

    # SBTi (index 3)
    (3, "SBT-001", "Near-term target must cover Scope 1 and 2 emissions", "validation", "blocker",
     {"check_type": "required_fields", "fields": ["scope1_target", "scope2_target"]}),
    (3, "SBT-002", "Near-term target must be 5-10 years from submission", "validation", "warning",
     {"check_type": "field_present", "field": "target_year"}),
    (3, "SBT-003", "1.5C pathway requires minimum 4.2% annual linear reduction", "threshold", "blocker",
     {"check_type": "numeric_range", "field": "annual_reduction_pct", "min": 4.2}),
    (3, "SBT-004", "Scope 3 target required if >40% of total emissions", "validation", "warning",
     {"check_type": "field_present", "field": "scope3_target"}),
    (3, "SBT-005", "Base year emissions must be verified", "validation", "warning",
     {"check_type": "field_present", "field": "base_year_verification"}),
    (3, "SBT-006", "Long-term net-zero target must be set", "validation", "warning",
     {"check_type": "field_present", "field": "net_zero_target_year"}),

    # UK SRS (index 4)
    (4, "SRS-001", "Climate-related risks and opportunities must be disclosed", "validation", "blocker",
     {"check_type": "field_present", "field": "climate_risks"}),
    (4, "SRS-002", "Governance arrangements for sustainability must be described", "validation", "blocker",
     {"check_type": "field_present", "field": "governance"}),
    (4, "SRS-003", "Strategy for managing climate-related risks", "validation", "blocker",
     {"check_type": "field_present", "field": "strategy"}),
    (4, "SRS-004", "Metrics and targets for measuring progress", "validation", "blocker",
     {"check_type": "field_present", "field": "metrics"}),
    (4, "SRS-005", "Transition plan disclosure", "validation", "warning",
     {"check_type": "field_present", "field": "transition_plan"}),

    # CDP (index 5)
    (5, "CDP-001", "Scope 1 and 2 emissions must be reported", "validation", "blocker",
     {"check_type": "required_fields", "fields": ["scope1_emissions", "scope2_emissions"]}),
    (5, "CDP-002", "Scope 3 categories must be screened", "validation", "warning",
     {"check_type": "field_present", "field": "scope3_screening"}),
    (5, "CDP-003", "Verification/assurance status must be stated", "validation", "warning",
     {"check_type": "field_present", "field": "verification_status"}),
    (5, "CDP-004", "Emissions reduction initiatives must be described", "validation", "warning",
     {"check_type": "field_present", "field": "reduction_initiatives"}),
    (5, "CDP-005", "Carbon pricing disclosure", "validation", "info",
     {"check_type": "field_present", "field": "carbon_pricing"}),

    # EPR (index 6)
    (6, "EPR-001", "Packaging data must be submitted for compliance year", "validation", "blocker",
     {"check_type": "required_fields", "fields": ["packaging_tonnage", "material_type"]}),
    (6, "EPR-002", "Material recyclability classification required", "validation", "blocker",
     {"check_type": "field_present", "field": "recyclability_class"}),
    (6, "EPR-003", "Producer obligation must be calculated", "validation", "warning",
     {"check_type": "field_present", "field": "obligation_amount"}),
    (6, "EPR-004", "Packaging waste recovery evidence", "validation", "warning",
     {"check_type": "field_present", "field": "recovery_evidence"}),

    # EUDR (index 7)
    (7, "EUDR-001", "Due diligence statement for relevant commodities", "validation", "blocker",
     {"check_type": "field_present", "field": "due_diligence_statement"}),
    (7, "EUDR-002", "Geolocation data for production areas", "validation", "blocker",
     {"check_type": "field_present", "field": "geolocation_data"}),
    (7, "EUDR-003", "Supply chain traceability documentation", "validation", "warning",
     {"check_type": "field_present", "field": "traceability_docs"}),
    (7, "EUDR-004", "Risk assessment for deforestation-free status", "validation", "warning",
     {"check_type": "field_present", "field": "risk_assessment"}),
    (7, "EUDR-005", "Compliance declaration before placing on market", "validation", "blocker",
     {"check_type": "field_present", "field": "compliance_declaration"}),
]


async def seed_frameworks(db: AsyncSession) -> None:
    """Seed frameworks and rules if they don't already exist."""
    existing_count = await db.execute(select(func.count(Framework.id)))
    if (existing_count.scalar() or 0) > 0:
        logger.info("Frameworks already seeded, skipping")
        return

    framework_records = []
    for fw_data in FRAMEWORKS:
        fw = Framework(**fw_data)
        db.add(fw)
        framework_records.append(fw)

    await db.flush()

    # Create rules
    for fw_idx, code, description, rule_type, severity, check_expr in RULES:
        rule = Rule(
            framework_id=framework_records[fw_idx].id,
            code=code,
            description=description,
            rule_type=rule_type,
            severity=severity,
            check_expression=check_expr,
            effective_date=date(2025, 1, 1),
        )
        db.add(rule)

    await db.flush()
    logger.info("Seeded %d frameworks and %d rules", len(FRAMEWORKS), len(RULES))


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

AGENTS = [
    {
        "name": "Carbon Auditor",
        "agent_type": "carbon_auditor",
        "gate_number": 1,
        "description": "Scans financial data, builds GHG inventory using DEFRA factors, calculates baseline emissions, and assigns confidence tiers.",
        "tool_permissions": ["read_invoices", "write_emissions", "read_defra_factors", "call_claude"],
    },
    {
        "name": "Strategy Builder",
        "agent_type": "strategy_builder",
        "gate_number": 2,
        "description": "Generates Carbon Reduction Plans aligned with PPN 006, calculates SBTi targets, and recommends applicable frameworks.",
        "tool_permissions": ["read_emissions", "write_crp", "read_frameworks", "call_claude"],
    },
    {
        "name": "Progress Tracker",
        "agent_type": "progress_tracker",
        "gate_number": 3,
        "description": "Monitors emissions trends against reduction targets, tracks KPIs, and flags deviations from the net-zero pathway.",
        "tool_permissions": ["read_emissions", "read_targets", "write_alerts"],
    },
    {
        "name": "Audit Prep",
        "agent_type": "audit_prep",
        "gate_number": 4,
        "description": "Prepares audit evidence packs, runs pre-audit compliance checks, and generates readiness assessments.",
        "tool_permissions": ["read_all", "write_evidence", "call_claude"],
    },
    {
        "name": "Report Writer",
        "agent_type": "report_writer",
        "gate_number": 5,
        "description": "Generates framework-specific compliance reports, disclosure documents, and submission-ready outputs.",
        "tool_permissions": ["read_all", "write_reports", "call_claude"],
    },
    {
        "name": "Security Auditor",
        "agent_type": "security_auditor",
        "gate_number": 6,
        "description": "Evaluates ISO 27001, GDPR, and NHS DSPT compliance. Runs security baseline checks and generates remediation plans.",
        "tool_permissions": ["read_security", "write_security", "call_claude"],
    },
]


async def seed_agents(db: AsyncSession) -> None:
    """Seed agent records if they don't already exist."""
    existing_count = await db.execute(select(func.count(Agent.id)))
    if (existing_count.scalar() or 0) > 0:
        logger.info("Agents already seeded, skipping")
        return

    for agent_data in AGENTS:
        agent = Agent(**agent_data)
        db.add(agent)

    await db.flush()
    logger.info("Seeded %d agents", len(AGENTS))
