from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional

from pydantic import BaseModel, Field


class EmissionsCreate(BaseModel):
    organisation_id: uuid.UUID
    reporting_year: int
    scope: int = Field(..., ge=1, le=3)
    category: str
    source: Optional[str] = None
    activity_data: Optional[Decimal] = None
    activity_unit: Optional[str] = None
    emission_factor: Optional[Decimal] = None
    emission_factor_source: Optional[str] = None
    co2e_tonnes: Optional[Decimal] = None
    confidence_tier: Optional[str] = None
    data_source: Optional[str] = None
    evidence_ref: Optional[str] = None
    notes: Optional[str] = None


class EmissionsUpdate(BaseModel):
    scope: Optional[int] = None
    category: Optional[str] = None
    source: Optional[str] = None
    activity_data: Optional[Decimal] = None
    activity_unit: Optional[str] = None
    emission_factor: Optional[Decimal] = None
    emission_factor_source: Optional[str] = None
    co2e_tonnes: Optional[Decimal] = None
    confidence_tier: Optional[str] = None
    data_source: Optional[str] = None
    evidence_ref: Optional[str] = None
    notes: Optional[str] = None


class EmissionsResponse(BaseModel):
    id: uuid.UUID
    organisation_id: uuid.UUID
    reporting_year: int
    scope: int
    category: str
    source: Optional[str] = None
    activity_data: Optional[Decimal] = None
    activity_unit: Optional[str] = None
    emission_factor: Optional[Decimal] = None
    emission_factor_source: Optional[str] = None
    co2e_tonnes: Optional[Decimal] = None
    confidence_tier: Optional[str] = None
    data_source: Optional[str] = None
    evidence_ref: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EmissionsBaselineSummary(BaseModel):
    scope1_total: Decimal
    scope2_total: Decimal
    scope3_total: Decimal
    total: Decimal
    reporting_year: int
    confidence_breakdown: Dict[str, int] = {}


class TrajectoryPoint(BaseModel):
    year: int
    actual: Optional[Decimal] = None
    target: Optional[Decimal] = None
