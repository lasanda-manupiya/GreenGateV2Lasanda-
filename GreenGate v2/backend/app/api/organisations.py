from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.database import get_db
from app.models.user import User
from app.schemas.organisation import (
    OrganisationCreate,
    OrganisationResponse,
    OrganisationUpdate,
)
from app.services.organisation_service import (
    create_organisation,
    get_gate_status,
    get_organisation,
    update_organisation,
)

router = APIRouter(prefix="/organisations", tags=["organisations"])


@router.post("/", response_model=OrganisationResponse, status_code=status.HTTP_201_CREATED)
async def create_org(
    data: OrganisationCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    """Create a new organisation."""
    org = await create_organisation(db, data)
    return org


@router.get("/{org_id}", response_model=OrganisationResponse)
async def get_org(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get an organisation by ID."""
    org = await get_organisation(db, org_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organisation not found")
    return org


@router.put("/{org_id}", response_model=OrganisationResponse)
async def update_org(
    org_id: uuid.UUID,
    data: OrganisationUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("editor")),
):
    """Update an organisation."""
    org = await update_organisation(db, org_id, data)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organisation not found")
    return org


@router.get("/{org_id}/gate-status")
async def get_org_gate_status(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get the current gate status and progress for an organisation."""
    result = await get_gate_status(db, org_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organisation not found")
    return result
