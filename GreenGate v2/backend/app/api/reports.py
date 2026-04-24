from __future__ import annotations

import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.database import get_db
from app.models.audit import AuditEntry
from app.models.emissions import EmissionsInventory
from app.models.framework import Framework
from app.models.submission import Submission
from app.models.user import User
from app.schemas.report import DashboardResponse, GateStatus, RegulatoryAlert
from app.services.emissions_service import get_baseline_summary
from app.services.evidence_service import generate_evidence_pack
from app.services.organisation_service import get_gate_status, get_organisation

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/{org_id}/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get the main dashboard data for an organisation."""
    org = await get_organisation(db, org_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organisation not found")

    # Gate statuses
    gate_data = await get_gate_status(db, org_id)
    gate_statuses = [
        GateStatus(**gs) for gs in gate_data.get("gate_statuses", [])
    ]

    # Emissions summary
    baseline = await get_baseline_summary(db, org_id)
    total_emissions = baseline.total if baseline else None
    emissions_by_scope = {}
    if baseline:
        emissions_by_scope = {
            "scope1": baseline.scope1_total,
            "scope2": baseline.scope2_total,
            "scope3": baseline.scope3_total,
        }

    # Compliance score (based on approved submissions / total possible)
    approved_count_result = await db.execute(
        select(func.count(Submission.id)).where(
            Submission.organisation_id == str(org_id),
            Submission.status == "approved",
        )
    )
    approved_count = approved_count_result.scalar() or 0
    total_frameworks = len(org.frameworks_enrolled or []) or 1
    compliance_score = min(100.0, (approved_count / (total_frameworks * 6)) * 100)

    # Recent activity
    audit_result = await db.execute(
        select(AuditEntry)
        .where(AuditEntry.organisation_id == str(org_id))
        .order_by(AuditEntry.timestamp.desc())
        .limit(10)
    )
    recent_entries = audit_result.scalars().all()
    recent_activity = [
        {
            "timestamp": e.timestamp.isoformat() if e.timestamp else None,
            "action": e.action,
            "actor_type": e.actor_type,
            "gate_number": e.gate_number,
            "governance_result": e.governance_result,
        }
        for e in recent_entries
    ]

    # Regulatory alerts (mock data for MVP)
    from app.api.regulatory import get_mock_alerts
    alerts = get_mock_alerts()

    return DashboardResponse(
        gate_statuses=gate_statuses,
        compliance_score=round(compliance_score, 1),
        total_emissions=total_emissions,
        emissions_by_scope=emissions_by_scope,
        recent_activity=recent_activity,
        regulatory_alerts=alerts,
    )


@router.get("/{org_id}/{framework_id}")
async def get_framework_report(
    org_id: uuid.UUID,
    framework_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get a framework-specific compliance report."""
    framework_result = await db.execute(
        select(Framework).where(Framework.id == framework_id)
    )
    framework = framework_result.scalar_one_or_none()
    if not framework:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Framework not found")

    # Get submissions for this framework
    submissions_result = await db.execute(
        select(Submission)
        .where(
            Submission.organisation_id == str(org_id),
            Submission.framework_id == str(framework_id),
        )
        .order_by(Submission.gate_number)
    )
    submissions = submissions_result.scalars().all()

    return {
        "organisation_id": str(org_id),
        "framework": {
            "id": str(framework.id),
            "name": framework.name,
            "version": framework.version,
            "description": framework.description,
        },
        "submissions": [
            {
                "id": str(s.id),
                "gate_number": s.gate_number,
                "status": s.status,
                "score": float(s.score) if s.score else None,
                "submitted_at": s.submitted_at.isoformat() if s.submitted_at else None,
            }
            for s in submissions
        ],
        "overall_status": "compliant" if all(
            s.status == "approved" for s in submissions
        ) and submissions else "in_progress",
    }


@router.post("/{org_id}/evidence-pack")
async def create_evidence_pack(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("editor")),
):
    """Generate an evidence pack ZIP for an organisation."""
    org = await get_organisation(db, org_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organisation not found")

    zip_path = await generate_evidence_pack(db, org_id)

    return FileResponse(
        path=str(zip_path),
        media_type="application/zip",
        filename=zip_path.name,
    )
