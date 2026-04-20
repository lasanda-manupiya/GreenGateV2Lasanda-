from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_role
from app.database import get_db
from app.models.organisation import Organisation
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter(prefix="/platform", tags=["platform-admin"])


class OrgSummary(BaseModel):
    id: str
    name: str
    sector: Optional[str] = None
    country: str
    current_gate: int
    onboarding_complete: bool
    user_count: int
    admin_email: Optional[str] = None
    created_at: str

    model_config = {"from_attributes": True}


class PlatformStats(BaseModel):
    total_organisations: int
    total_users: int
    active_users: int
    organisations: List[OrgSummary]


@router.get("/stats", response_model=PlatformStats)
async def get_platform_stats(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("superadmin")),
):
    """Get platform-wide statistics. Superadmin only."""
    # Total orgs
    org_count = await db.execute(select(func.count(Organisation.id)))
    total_orgs = org_count.scalar() or 0

    # Total users
    user_count = await db.execute(select(func.count(User.id)))
    total_users = user_count.scalar() or 0

    # Active users
    active_count = await db.execute(
        select(func.count(User.id)).where(User.is_active == True)
    )
    active_users = active_count.scalar() or 0

    # All orgs with user counts
    orgs_result = await db.execute(
        select(Organisation).order_by(Organisation.created_at.desc())
    )
    orgs = list(orgs_result.scalars().all())

    org_summaries = []
    for org in orgs:
        # Count users per org
        uc = await db.execute(
            select(func.count(User.id)).where(User.organisation_id == org.id)
        )
        org_user_count = uc.scalar() or 0

        # Find org admin email
        admin_result = await db.execute(
            select(User.email)
            .where(User.organisation_id == org.id)
            .where(User.role.in_(["admin", "superadmin"]))
            .order_by(User.created_at)
            .limit(1)
        )
        admin_email = admin_result.scalar_one_or_none()

        org_summaries.append(OrgSummary(
            id=org.id,
            name=org.name,
            sector=org.sector,
            country=org.country,
            current_gate=org.current_gate,
            onboarding_complete=org.onboarding_complete,
            user_count=org_user_count,
            admin_email=admin_email,
            created_at=str(org.created_at),
        ))

    return PlatformStats(
        total_organisations=total_orgs,
        total_users=total_users,
        active_users=active_users,
        organisations=org_summaries,
    )


@router.get("/organisations/{org_id}/users", response_model=List[UserResponse])
async def get_org_users(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("superadmin")),
):
    """List all users in any organisation. Superadmin only."""
    result = await db.execute(
        select(User)
        .where(User.organisation_id == org_id)
        .order_by(User.created_at)
    )
    return list(result.scalars().all())
