from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=4)
    full_name: str = Field(..., min_length=1, max_length=255)
    role: str = "viewer"
    organisation_name: Optional[str] = None
    organisation_id: Optional[str] = None
    sector: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    token: str


class UserResponse(BaseModel):
    id: str
    organisation_id: str
    email: str
    full_name: str
    role: str
    is_director: bool
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
