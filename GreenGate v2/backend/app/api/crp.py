from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.database import get_db
from app.models.agent import Agent
from app.models.user import User
from app.agents.claude_client import ClaudeClient
from app.agents.strategy_builder import StrategyBuilder
from app.config import settings
from app.governance.engine import GovernanceEngine
from app.services.crp_service import get_latest_crp

router = APIRouter(prefix="/crp", tags=["crp"])


@router.post("/generate")
async def generate_crp(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("editor")),
):
    """Generate a Carbon Reduction Plan using the Strategy Builder agent."""
    # Find the Strategy Builder agent
    result = await db.execute(
        select(Agent).where(Agent.agent_type == "strategy_builder")
    )
    agent_record = result.scalar_one_or_none()
    if not agent_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy Builder agent not found. Run seed data first.",
        )

    governance_engine = GovernanceEngine(db)
    claude_client = ClaudeClient(settings.ANTHROPIC_API_KEY)
    agent = StrategyBuilder(agent_record, governance_engine, claude_client, db)

    agent_result = await agent.run_action(
        org_id,
        "generate_crp",
        {"organisation_id": str(org_id)},
    )

    return {
        "status": agent_result.status,
        "crp": agent_result.data,
        "audit_entries": agent_result.audit_entries,
    }


@router.get("/{org_id}/latest")
async def get_latest(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get the latest CRP document for an organisation."""
    crp = await get_latest_crp(db, org_id)
    if not crp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No CRP document found for this organisation",
        )
    return {
        "id": str(crp.id),
        "organisation_id": str(crp.organisation_id),
        "version": crp.version,
        "status": crp.status,
        "content": crp.content,
        "ppn006_aligned": crp.ppn006_aligned,
        "sbti_target": crp.sbti_target,
        "director_approved": crp.director_approved,
        "created_at": crp.created_at.isoformat() if crp.created_at else None,
        "updated_at": crp.updated_at.isoformat() if crp.updated_at else None,
    }
