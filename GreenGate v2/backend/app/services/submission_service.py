from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.submission import Submission
from app.models.audit import AuditEntry
from app.schemas.submission import SubmissionCreate, SubmissionStatusUpdate


async def create_submission(
    db: AsyncSession, data: SubmissionCreate, user_id: uuid.UUID
) -> Submission:
    submission = Submission(
        organisation_id=data.organisation_id,
        gate_number=data.gate_number,
        framework_id=data.framework_id,
        content=data.content,
        submitted_by=user_id,
    )
    db.add(submission)
    await db.flush()
    return submission


async def get_submission(db: AsyncSession, submission_id: uuid.UUID) -> Optional[Submission]:
    result = await db.execute(
        select(Submission).where(Submission.id == submission_id)
    )
    return result.scalar_one_or_none()


async def get_submission_with_audit(
    db: AsyncSession, submission_id: uuid.UUID
) -> Optional[dict]:
    submission = await get_submission(db, submission_id)
    if not submission:
        return None

    # Get related audit entries
    audit_result = await db.execute(
        select(AuditEntry)
        .where(
            AuditEntry.resource_type == "submission",
            AuditEntry.resource_id == str(submission_id),
        )
        .order_by(AuditEntry.timestamp.desc())
    )
    audit_entries = list(audit_result.scalars().all())

    return {
        "submission": submission,
        "audit_trail": audit_entries,
    }


async def update_submission_status(
    db: AsyncSession, submission_id: uuid.UUID, data: SubmissionStatusUpdate
) -> Optional[Submission]:
    submission = await get_submission(db, submission_id)
    if not submission:
        return None

    submission.status = data.status
    if data.feedback:
        submission.feedback = data.feedback
    if data.score is not None:
        submission.score = data.score

    now = datetime.now(timezone.utc)
    if data.status == "submitted":
        submission.submitted_at = now
    elif data.status in ("approved", "rejected"):
        submission.reviewed_at = now

    await db.flush()
    return submission
