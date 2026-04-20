from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditEntry


class AuditLogger:
    """Append-only audit logger for governance actions."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def log(
        self,
        actor_type: str,
        actor_id: str,
        org_id: uuid.UUID,
        action: str,
        gate_number: Optional[int] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[dict] = None,
        governance_result: Optional[str] = None,
        redacted_fields: Optional[List[str]] = None,
    ) -> AuditEntry:
        """Insert an audit entry. Never updates existing entries."""
        entry = AuditEntry(
            organisation_id=str(org_id),
            timestamp=datetime.now(timezone.utc),
            actor_type=actor_type,
            actor_id=actor_id,
            action=action,
            gate_number=gate_number,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            governance_result=governance_result,
            redacted_fields=redacted_fields or [],
        )
        self.db.add(entry)
        await self.db.flush()
        return entry

    async def get_entries(
        self,
        org_id: uuid.UUID,
        gate_number: Optional[int] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[AuditEntry]:
        """Retrieve audit entries with filters."""
        query = (
            select(AuditEntry)
            .where(AuditEntry.organisation_id == str(org_id))
            .order_by(AuditEntry.timestamp.desc())
        )

        if gate_number is not None:
            query = query.where(AuditEntry.gate_number == gate_number)
        if from_date:
            query = query.where(AuditEntry.timestamp >= from_date)
        if to_date:
            query = query.where(AuditEntry.timestamp <= to_date)

        query = query.limit(limit).offset(offset)
        result = await self.db.execute(query)
        return list(result.scalars().all())
