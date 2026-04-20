from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organisation import Organisation
from app.models.submission import Submission
from app.models.emissions import EmissionsInventory
from app.schemas.organisation import OrganisationCreate, OrganisationUpdate


GATE_DEFINITIONS = [
    {"gate_number": 1, "name": "Carbon Baseline", "agent": "Carbon Auditor"},
    {"gate_number": 2, "name": "Net-Zero Strategy", "agent": "Strategy Builder"},
    {"gate_number": 3, "name": "Progress Tracking", "agent": "Progress Tracker"},
    {"gate_number": 4, "name": "Audit Readiness", "agent": "Audit Prep"},
    {"gate_number": 5, "name": "Reporting & Disclosure", "agent": "Report Writer"},
    {"gate_number": 6, "name": "Security & Data Governance", "agent": "Security Auditor"},
]


async def create_organisation(db: AsyncSession, data: OrganisationCreate) -> Organisation:
    org = Organisation(
        name=data.name,
        company_number=data.company_number,
        sector=data.sector,
        employee_count=data.employee_count,
        turnover_band=data.turnover_band,
        country=data.country,
        reporting_year_start=data.reporting_year_start,
        frameworks_enrolled=data.frameworks_enrolled or [],
    )
    db.add(org)
    await db.flush()
    return org


async def get_organisation(db: AsyncSession, org_id: uuid.UUID) -> Optional[Organisation]:
    result = await db.execute(select(Organisation).where(Organisation.id == org_id))
    return result.scalar_one_or_none()


async def update_organisation(
    db: AsyncSession, org_id: uuid.UUID, data: OrganisationUpdate
) -> Optional[Organisation]:
    org = await get_organisation(db, org_id)
    if not org:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(org, field, value)
    await db.flush()
    return org


async def get_gate_status(db: AsyncSession, org_id: uuid.UUID) -> dict:
    org = await get_organisation(db, org_id)
    if not org:
        return {}

    # Count approved submissions per gate
    result = await db.execute(
        select(Submission.gate_number, func.count(Submission.id))
        .where(Submission.organisation_id == org_id, Submission.status == "approved")
        .group_by(Submission.gate_number)
    )
    approved_by_gate = dict(result.all())

    # Check if emissions data exists (for gate 1 progress)
    emissions_count_result = await db.execute(
        select(func.count(EmissionsInventory.id)).where(
            EmissionsInventory.organisation_id == org_id
        )
    )
    emissions_count = emissions_count_result.scalar() or 0

    gate_statuses = []
    for gate_def in GATE_DEFINITIONS:
        gate_num = gate_def["gate_number"]
        approved_count = approved_by_gate.get(gate_num, 0)

        if gate_num < org.current_gate:
            status = "completed"
            progress = 100.0
        elif gate_num == org.current_gate:
            status = "in_progress"
            if gate_num == 1:
                progress = min(100.0, (emissions_count / 10) * 100) if emissions_count else 0.0
            else:
                progress = min(100.0, approved_count * 25.0)
        else:
            status = "not_started"
            progress = 0.0

        gate_statuses.append({
            "gate_number": gate_num,
            "name": gate_def["name"],
            "status": status,
            "progress_pct": round(progress, 1),
            "agent_name": gate_def["agent"],
        })

    return {
        "organisation_id": str(org_id),
        "current_gate": org.current_gate,
        "gate_statuses": gate_statuses,
    }
