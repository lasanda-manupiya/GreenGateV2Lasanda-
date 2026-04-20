from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.database import get_db
from app.models.user import User
from app.schemas.emissions import (
    EmissionsBaselineSummary,
    EmissionsCreate,
    EmissionsResponse,
    TrajectoryPoint,
)
from app.services.emissions_service import (
    create_emissions_entry,
    get_baseline_summary,
    get_trajectory,
    list_emissions,
)

router = APIRouter(prefix="/emissions", tags=["emissions"])


@router.post("/inventory", response_model=EmissionsResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory_entry(
    data: EmissionsCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("editor")),
):
    """Create a new emissions inventory entry."""
    entry = await create_emissions_entry(db, data)
    return entry


@router.get("/inventory", response_model=List[EmissionsResponse])
async def get_inventory(
    org_id: Optional[uuid.UUID] = Query(None),
    scope: Optional[int] = Query(None, ge=1, le=3),
    year: Optional[int] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List emissions inventory entries with optional filters."""
    entries = await list_emissions(db, org_id=org_id, scope=scope, year=year, limit=limit, offset=offset)
    return entries


@router.get("/{org_id}/baseline", response_model=EmissionsBaselineSummary)
async def get_org_baseline(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get the emissions baseline summary for an organisation."""
    summary = await get_baseline_summary(db, org_id)
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No emissions data found for this organisation",
        )
    return summary


@router.get("/{org_id}/trajectory", response_model=List[TrajectoryPoint])
async def get_org_trajectory(
    org_id: uuid.UUID,
    target_year: int = Query(2030),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get emissions trajectory vs SBTi targets."""
    points = await get_trajectory(db, org_id, target_year=target_year)
    if not points:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No emissions data found for trajectory calculation",
        )
    return points
