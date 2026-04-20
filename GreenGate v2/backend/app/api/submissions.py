from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.database import get_db
from app.models.user import User
from app.schemas.submission import (
    SubmissionCreate,
    SubmissionResponse,
    SubmissionStatusUpdate,
)
from app.services.submission_service import (
    create_submission,
    get_submission_with_audit,
    update_submission_status,
)

router = APIRouter(prefix="/submissions", tags=["submissions"])


@router.post("/", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
async def create_new_submission(
    data: SubmissionCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("editor")),
):
    """Create a new gate submission."""
    submission = await create_submission(db, data, user.id)
    return submission


@router.get("/{submission_id}")
async def get_submission_detail(
    submission_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get a submission with its full audit trail."""
    result = await get_submission_with_audit(db, submission_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found"
        )

    submission = result["submission"]
    audit_trail = result["audit_trail"]

    return {
        "id": str(submission.id),
        "organisation_id": str(submission.organisation_id),
        "gate_number": submission.gate_number,
        "framework_id": str(submission.framework_id),
        "status": submission.status,
        "submitted_by": str(submission.submitted_by) if submission.submitted_by else None,
        "content": submission.content,
        "score": float(submission.score) if submission.score else None,
        "feedback": submission.feedback,
        "submitted_at": submission.submitted_at.isoformat() if submission.submitted_at else None,
        "reviewed_at": submission.reviewed_at.isoformat() if submission.reviewed_at else None,
        "created_at": submission.created_at.isoformat() if submission.created_at else None,
        "audit_trail": [
            {
                "id": str(a.id),
                "timestamp": a.timestamp.isoformat() if a.timestamp else None,
                "actor_type": a.actor_type,
                "action": a.action,
                "governance_result": a.governance_result,
                "details": a.details,
            }
            for a in audit_trail
        ],
    }


@router.patch("/{submission_id}/status", response_model=SubmissionResponse)
async def update_status(
    submission_id: uuid.UUID,
    data: SubmissionStatusUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("editor")),
):
    """Update the status of a submission."""
    submission = await update_submission_status(db, submission_id, data)
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found"
        )
    return submission
