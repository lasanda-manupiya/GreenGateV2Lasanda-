from __future__ import annotations

import uuid
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.emissions import EmissionsInventory
from app.schemas.emissions import EmissionsCreate, EmissionsUpdate, EmissionsBaselineSummary, TrajectoryPoint


async def create_emissions_entry(db: AsyncSession, data: EmissionsCreate) -> EmissionsInventory:
    entry = EmissionsInventory(**data.model_dump())
    db.add(entry)
    await db.flush()
    return entry


async def list_emissions(
    db: AsyncSession,
    org_id: Optional[uuid.UUID] = None,
    scope: Optional[int] = None,
    year: Optional[int] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[EmissionsInventory]:
    query = select(EmissionsInventory)
    if org_id:
        query = query.where(EmissionsInventory.organisation_id == str(org_id))
    if scope:
        query = query.where(EmissionsInventory.scope == scope)
    if year:
        query = query.where(EmissionsInventory.reporting_year == year)
    query = query.order_by(EmissionsInventory.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_baseline_summary(
    db: AsyncSession, org_id: uuid.UUID
) -> Optional[EmissionsBaselineSummary]:
    # Find the earliest reporting year with data (baseline year)
    year_result = await db.execute(
        select(func.min(EmissionsInventory.reporting_year)).where(
            EmissionsInventory.organisation_id == str(org_id)
        )
    )
    baseline_year = year_result.scalar()
    if not baseline_year:
        return None

    # Sum by scope
    scope_totals = {}
    for scope_num in [1, 2, 3]:
        total_result = await db.execute(
            select(func.coalesce(func.sum(EmissionsInventory.co2e_tonnes), 0)).where(
                EmissionsInventory.organisation_id == str(org_id),
                EmissionsInventory.reporting_year == baseline_year,
                EmissionsInventory.scope == scope_num,
            )
        )
        scope_totals[scope_num] = total_result.scalar() or Decimal("0")

    # Confidence breakdown
    conf_result = await db.execute(
        select(EmissionsInventory.confidence_tier, func.count(EmissionsInventory.id))
        .where(
            EmissionsInventory.organisation_id == str(org_id),
            EmissionsInventory.reporting_year == baseline_year,
        )
        .group_by(EmissionsInventory.confidence_tier)
    )
    confidence_breakdown = {
        tier or "unassigned": count for tier, count in conf_result.all()
    }

    total = scope_totals[1] + scope_totals[2] + scope_totals[3]

    return EmissionsBaselineSummary(
        scope1_total=scope_totals[1],
        scope2_total=scope_totals[2],
        scope3_total=scope_totals[3],
        total=total,
        reporting_year=baseline_year,
        confidence_breakdown=confidence_breakdown,
    )


async def get_trajectory(
    db: AsyncSession, org_id: uuid.UUID, target_year: int = 2030
) -> List[TrajectoryPoint]:
    # Get all years of emissions data
    year_totals_result = await db.execute(
        select(
            EmissionsInventory.reporting_year,
            func.sum(EmissionsInventory.co2e_tonnes),
        )
        .where(EmissionsInventory.organisation_id == str(org_id))
        .group_by(EmissionsInventory.reporting_year)
        .order_by(EmissionsInventory.reporting_year)
    )
    year_totals = {year: total for year, total in year_totals_result.all()}

    if not year_totals:
        return []

    base_year = min(year_totals.keys())
    base_total = year_totals[base_year]

    # SBTi 1.5C pathway: ~4.2% annual linear reduction
    annual_reduction_rate = Decimal("0.042")

    points = []
    for year in range(base_year, target_year + 1):
        years_elapsed = year - base_year
        target_value = base_total * (1 - annual_reduction_rate * years_elapsed)
        target_value = max(target_value, Decimal("0"))

        actual_value = year_totals.get(year)

        points.append(TrajectoryPoint(
            year=year,
            actual=actual_value,
            target=round(target_value, 2),
        ))

    return points
