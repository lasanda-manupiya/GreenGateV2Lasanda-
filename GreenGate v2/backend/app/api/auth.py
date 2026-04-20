from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.organisation import Organisation
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, TokenResponse, UserResponse, RefreshRequest
from app.services.auth_service import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user. Creates an organisation if organisation_name is provided."""
    # Check if email already exists
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Create or find organisation
    if data.organisation_id:
        org_id = data.organisation_id
        org = await db.execute(select(Organisation).where(Organisation.id == org_id))
        if not org.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organisation not found",
            )
    elif data.organisation_name:
        org = Organisation(name=data.organisation_name, sector=getattr(data, 'sector', None))
        db.add(org)
        await db.flush()
        org_id = org.id
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either organisation_id or organisation_name is required",
        )

    # First user in a new org becomes admin (company admin)
    # Only Kevin (platform superadmin) has the superadmin role
    user_count = await db.execute(
        select(func.count(User.id)).where(User.organisation_id == org_id)
    )
    is_first_user = (user_count.scalar() or 0) == 0
    role = "admin" if is_first_user else data.role

    user = User(
        organisation_id=org_id,
        email=data.email,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        role=role,
    )
    db.add(user)
    await db.flush()

    return user


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return JWT tokens."""
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    access_token = create_access_token(
        str(user.id), str(user.organisation_id), user.role
    )
    refresh_token = create_refresh_token(str(user.id), str(user.organisation_id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Refresh an access token using a valid refresh token."""
    try:
        payload = decode_token(data.token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    access_token = create_access_token(
        str(user.id), str(user.organisation_id), user.role
    )
    new_refresh_token = create_refresh_token(str(user.id), str(user.organisation_id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    """Return the currently authenticated user."""
    return user
