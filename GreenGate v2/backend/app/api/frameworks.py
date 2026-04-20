from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.database import get_db
from app.models.framework import Framework, Rule
from app.models.user import User

router = APIRouter(prefix="/frameworks", tags=["frameworks"])


@router.get("/")
async def list_frameworks(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List all active frameworks."""
    result = await db.execute(
        select(Framework).where(Framework.is_active.is_(True)).order_by(Framework.name)
    )
    frameworks = result.scalars().all()
    return [
        {
            "id": str(f.id),
            "name": f.name,
            "version": f.version,
            "description": f.description,
            "jurisdiction": f.jurisdiction,
            "gate_number": f.gate_number,
            "is_active": f.is_active,
            "created_at": f.created_at.isoformat() if f.created_at else None,
        }
        for f in frameworks
    ]


@router.get("/{framework_id}/rules")
async def list_framework_rules(
    framework_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List all rules for a given framework."""
    framework = await db.execute(select(Framework).where(Framework.id == framework_id))
    if not framework.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Framework not found")

    result = await db.execute(
        select(Rule)
        .where(Rule.framework_id == framework_id, Rule.is_active.is_(True))
        .order_by(Rule.code)
    )
    rules = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "framework_id": str(r.framework_id),
            "code": r.code,
            "description": r.description,
            "rule_type": r.rule_type,
            "severity": r.severity,
            "check_expression": r.check_expression,
            "effective_date": r.effective_date.isoformat() if r.effective_date else None,
            "expiry_date": r.expiry_date.isoformat() if r.expiry_date else None,
            "is_active": r.is_active,
        }
        for r in rules
    ]


@router.post("/{framework_id}/rules/upload")
async def upload_policy_doc(
    framework_id: uuid.UUID,
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    """Upload a policy document and extract rules (stub for MVP)."""
    framework_result = await db.execute(
        select(Framework).where(Framework.id == framework_id)
    )
    framework = framework_result.scalar_one_or_none()
    if not framework:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Framework not found")

    content = await file.read()
    file_size = len(content)

    # Stub: return mock extracted rules
    mock_rules = [
        {
            "code": f"{framework.name[:3].upper()}-EXT-001",
            "description": f"Extracted rule from uploaded document for {framework.name}",
            "rule_type": "validation",
            "severity": "warning",
            "check_expression": {"check_type": "field_present", "field": "evidence_ref"},
        },
        {
            "code": f"{framework.name[:3].upper()}-EXT-002",
            "description": f"Compliance threshold rule from {framework.name} policy",
            "rule_type": "threshold",
            "severity": "blocker",
            "check_expression": {
                "check_type": "threshold",
                "field": "compliance_score",
                "threshold": 70,
                "operator": ">=",
            },
        },
    ]

    return {
        "message": f"Policy document processed ({file_size} bytes)",
        "framework": framework.name,
        "extracted_rules": mock_rules,
        "note": "These are mock-extracted rules for MVP. Full NLP extraction coming in v2.",
    }


@router.put("/{framework_id}/rules/{rule_id}")
async def update_rule(
    framework_id: uuid.UUID,
    rule_id: uuid.UUID,
    updates: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    """Update an existing rule."""
    result = await db.execute(
        select(Rule).where(Rule.id == rule_id, Rule.framework_id == framework_id)
    )
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")

    allowed_fields = {
        "description", "rule_type", "severity", "check_expression",
        "effective_date", "expiry_date", "is_active",
    }
    for field, value in updates.items():
        if field in allowed_fields:
            setattr(rule, field, value)

    await db.flush()
    return {
        "id": str(rule.id),
        "code": rule.code,
        "description": rule.description,
        "rule_type": rule.rule_type,
        "severity": rule.severity,
        "check_expression": rule.check_expression,
        "is_active": rule.is_active,
        "message": "Rule updated successfully",
    }
