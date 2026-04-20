from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class SubmissionCreate(BaseModel):
    organisation_id: uuid.UUID
    gate_number: int
    framework_id: uuid.UUID
    content: Optional[dict] = None


class SubmissionStatusUpdate(BaseModel):
    status: str  # draft / submitted / under_review / approved / rejected
    feedback: Optional[str] = None
    score: Optional[Decimal] = None


class SubmissionResponse(BaseModel):
    id: uuid.UUID
    organisation_id: uuid.UUID
    gate_number: int
    framework_id: uuid.UUID
    status: str
    submitted_by: Optional[uuid.UUID] = None
    content: Optional[dict] = None
    score: Optional[Decimal] = None
    feedback: Optional[str] = None
    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}
