from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AgentResponse(BaseModel):
    id: uuid.UUID
    name: str
    agent_type: str
    gate_number: int
    description: Optional[str] = None
    status: str
    policy_profile: Optional[dict] = None
    tool_permissions: Optional[list] = None
    last_active_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AgentRunRequest(BaseModel):
    action: str
    payload: dict = {}


class AgentRunResponse(BaseModel):
    status: str
    result: dict = {}
    audit_entries: list = []
