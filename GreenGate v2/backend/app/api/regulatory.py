from __future__ import annotations

from datetime import date
from typing import List

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.report import RegulatoryAlert

router = APIRouter(prefix="/regulatory", tags=["regulatory"])


def get_mock_alerts() -> List[RegulatoryAlert]:
    """Return mock regulatory alerts for MVP."""
    return [
        RegulatoryAlert(
            id="RA-001",
            title="UK Sustainability Reporting Standards (UK SRS) finalisation",
            framework="UK SRS",
            severity="high",
            deadline=date(2026, 7, 1),
            description=(
                "The UK Endorsement Board is expected to finalise UK SRS based on "
                "ISSB S1/S2 standards. Companies meeting size thresholds should begin "
                "preparing for mandatory climate-related disclosures."
            ),
        ),
        RegulatoryAlert(
            id="RA-002",
            title="PPN 006 Carbon Reduction Plan requirement update",
            framework="PPN 006",
            severity="critical",
            deadline=date(2026, 4, 1),
            description=(
                "Updated PPN 006 Technical Standard requires enhanced Carbon Reduction "
                "Plans for all central government contracts over GBP 5 million. Plans "
                "must now include Scope 3 emissions and SBTi-aligned targets."
            ),
        ),
        RegulatoryAlert(
            id="RA-003",
            title="NHS Evergreen Sustainable Supplier Assessment",
            framework="NHS Evergreen",
            severity="high",
            deadline=date(2026, 6, 30),
            description=(
                "NHS England requires all suppliers to complete the Evergreen "
                "Sustainable Supplier Assessment. Net-zero roadmaps must demonstrate "
                "alignment with the NHS target of net zero by 2045 for supply chain."
            ),
        ),
        RegulatoryAlert(
            id="RA-004",
            title="EU Deforestation Regulation (EUDR) delayed enforcement",
            framework="EUDR",
            severity="medium",
            deadline=date(2026, 12, 30),
            description=(
                "EUDR due diligence requirements now apply. Companies placing or "
                "exporting relevant commodities must demonstrate products are "
                "deforestation-free with full supply chain traceability."
            ),
        ),
        RegulatoryAlert(
            id="RA-005",
            title="CDP 2026 questionnaire deadline",
            framework="CDP",
            severity="medium",
            deadline=date(2026, 7, 31),
            description=(
                "CDP climate change questionnaire submissions open in April 2026. "
                "Updated scoring methodology emphasises transition plans and "
                "Scope 3 data quality. Early preparation is recommended."
            ),
        ),
        RegulatoryAlert(
            id="RA-006",
            title="Extended Producer Responsibility (EPR) packaging data",
            framework="EPR",
            severity="high",
            deadline=date(2026, 4, 1),
            description=(
                "Obligated producers must submit packaging data for the 2025 "
                "compliance year. New modulated fees based on recyclability come "
                "into effect. Data must be submitted via the approved scheme."
            ),
        ),
    ]


@router.get("/alerts", response_model=List[RegulatoryAlert])
async def get_regulatory_alerts(
    user: User = Depends(get_current_user),
):
    """Get current regulatory alerts and upcoming deadlines."""
    return get_mock_alerts()
