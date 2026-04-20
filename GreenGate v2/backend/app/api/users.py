from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role, ROLE_HIERARCHY
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse
from app.services.auth_service import hash_password

router = APIRouter(prefix="/users", tags=["users"])


class InviteUserRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    full_name: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=4)
    role: str = Field(default="viewer")


class UpdateUserRoleRequest(BaseModel):
    role: str = Field(...)


class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int


@router.get("/", response_model=UserListResponse)
async def list_users(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    """List all users in the current user's organisation. Requires admin or superadmin."""
    # Count total
    count_result = await db.execute(
        select(func.count(User.id)).where(User.organisation_id == user.organisation_id)
    )
    total = count_result.scalar() or 0

    # Fetch users
    result = await db.execute(
        select(User)
        .where(User.organisation_id == user.organisation_id)
        .order_by(User.created_at)
        .offset(offset)
        .limit(limit)
    )
    users = list(result.scalars().all())

    return UserListResponse(users=users, total=total)


@router.post("/invite", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def invite_user(
    data: InviteUserRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    """Invite a new user to the current user's organisation. Requires admin or superadmin.

    Admins can create viewers and editors.
    Only superadmins can create admins.
    """
    # Check email uniqueness
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Validate role
    valid_roles = ["viewer", "editor", "admin"]
    if data.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be one of: %s" % ", ".join(valid_roles),
        )

    # Only superadmin can create admin users
    if data.role == "admin" and user.role != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmins can create admin users",
        )

    new_user = User(
        organisation_id=user.organisation_id,
        email=data.email,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        role=data.role,
    )
    db.add(new_user)
    await db.flush()
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.put("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: str,
    data: UpdateUserRoleRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    """Update a user's role. Admins can set viewer/editor. Superadmins can set admin too."""
    # Find target user
    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()

    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Must be in same org
    if target.organisation_id != user.organisation_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not in your organisation")

    # Can't change your own role
    if target.id == user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot change your own role")

    # Can't change a superadmin
    if target.role == "superadmin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot modify superadmin role")

    # Validate new role
    valid_roles = ["viewer", "editor", "admin"]
    if data.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be one of: %s" % ", ".join(valid_roles),
        )

    # Only superadmin can promote to admin
    if data.role == "admin" and user.role != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmins can promote users to admin",
        )

    target.role = data.role
    await db.flush()
    await db.commit()
    await db.refresh(target)

    return target


@router.put("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    """Deactivate a user account. They will no longer be able to log in."""
    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()

    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if target.organisation_id != user.organisation_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not in your organisation")

    if target.id == user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot deactivate yourself")

    if target.role == "superadmin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot deactivate superadmin")

    target.is_active = not target.is_active
    await db.flush()
    await db.commit()
    await db.refresh(target)

    return target
