from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional

from pydantic import BaseModel


class GateStatus(BaseModel):
    gate_number: int
    name: str
    status: str  # not_started / in_progress / completed / blocked
    progress_pct: float
    agent_name: Optional[str] = None


class RegulatoryAlert(BaseModel):
    id: str
    title: str
    framework: str
    severity: str  # critical / high / medium / low
    deadline: Optional[date] = None
    description: str


class DashboardResponse(BaseModel):
    gate_statuses: List[GateStatus]
    compliance_score: float
    total_emissions: Optional[Decimal] = None
    emissions_by_scope: Dict[str, Decimal] = {}
    recent_activity: List[dict] = []
    regulatory_alerts: List[RegulatoryAlert] = []
