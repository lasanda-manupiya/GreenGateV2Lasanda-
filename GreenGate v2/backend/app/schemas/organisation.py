from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class OrganisationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    company_number: Optional[str] = None
    sector: Optional[str] = None
    employee_count: Optional[int] = None
    turnover_band: Optional[str] = None
    country: str = "UK"
    reporting_year_start: Optional[str] = None
    frameworks_enrolled: Optional[List[str]] = None


class OrganisationUpdate(BaseModel):
    name: Optional[str] = None
    company_number: Optional[str] = None
    sector: Optional[str] = None
    employee_count: Optional[int] = None
    turnover_band: Optional[str] = None
    country: Optional[str] = None
    reporting_year_start: Optional[str] = None
    current_gate: Optional[int] = None
    onboarding_complete: Optional[bool] = None
    frameworks_enrolled: Optional[List[str]] = None


class OrganisationResponse(BaseModel):
    id: uuid.UUID
    name: str
    company_number: Optional[str] = None
    sector: Optional[str] = None
    employee_count: Optional[int] = None
    turnover_band: Optional[str] = None
    country: str
    reporting_year_start: Optional[str] = None
    current_gate: int
    onboarding_complete: bool
    frameworks_enrolled: Optional[list] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OrganisationListResponse(BaseModel):
    items: List[OrganisationResponse]
    total: int
