from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.database import get_db
from app.models.agent import Agent
from app.models.user import User
from app.schemas.agent import AgentResponse, AgentRunRequest, AgentRunResponse
from app.governance.engine import GovernanceEngine
from app.agents.claude_client import ClaudeClient
from app.agents.carbon_auditor import CarbonAuditor
from app.agents.strategy_builder import StrategyBuilder
from app.agents.progress_tracker import ProgressTracker
from app.agents.audit_prep import AuditPrep
from app.agents.report_writer import ReportWriter
from app.agents.security_auditor import SecurityAuditor
from app.config import settings

router = APIRouter(prefix="/agents", tags=["agents"])

AGENT_TYPE_MAP = {
    "carbon_auditor": CarbonAuditor,
    "strategy_builder": StrategyBuilder,
    "progress_tracker": ProgressTracker,
    "audit_prep": AuditPrep,
    "report_writer": ReportWriter,
    "security_auditor": SecurityAuditor,
}


@router.get("/llm/runtime")
async def get_llm_runtime(
    user: User = Depends(get_current_user),
):
    """Get current LLM runtime mode (openai/anthropic/mock) for diagnostics."""
    client = ClaudeClient(
        anthropic_api_key=settings.ANTHROPIC_API_KEY,
        provider=settings.LLM_PROVIDER,
        openai_api_key=settings.OPENAI_API_KEY,
        openai_model=settings.OPENAI_MODEL,
    )
    return client.runtime_info()


@router.get("/", response_model=List[AgentResponse])
async def list_agents(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List all agents."""
    result = await db.execute(select(Agent).order_by(Agent.gate_number))
    return list(result.scalars().all())


@router.get("/{agent_id}/status")
async def get_agent_status(
    agent_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get an agent's current status."""
    result = await db.execute(select(Agent).where(Agent.id == str(agent_id)))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return {
        "id": str(agent.id),
        "name": agent.name,
        "status": agent.status,
        "last_active_at": agent.last_active_at.isoformat() if agent.last_active_at else None,
    }


@router.post("/{agent_id}/run", response_model=AgentRunResponse)
async def run_agent(
    agent_id: uuid.UUID,
    request: AgentRunRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("editor")),
):
    """Run an agent action. Governance is enforced here."""
    result = await db.execute(select(Agent).where(Agent.id == str(agent_id)))
    agent_record = result.scalar_one_or_none()
    if not agent_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    agent_cls = AGENT_TYPE_MAP.get(agent_record.agent_type)
    if not agent_cls:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agent type '{agent_record.agent_type}' not implemented",
        )

    # Set up governance and Claude client
    governance_engine = GovernanceEngine(db)
    claude_client = ClaudeClient(
        anthropic_api_key=settings.ANTHROPIC_API_KEY,
        provider=settings.LLM_PROVIDER,
        openai_api_key=settings.OPENAI_API_KEY,
        openai_model=settings.OPENAI_MODEL,
    )

    # Instantiate agent
    agent_instance = agent_cls(agent_record, governance_engine, claude_client, db)

    # Update agent status
    agent_record.status = "running"
    agent_record.last_active_at = datetime.now(timezone.utc)
    await db.flush()

    try:
        org_id = uuid.UUID(request.payload.get("organisation_id", str(user.organisation_id)))
        agent_result = await agent_instance.run_action(org_id, request.action, request.payload)

        agent_record.status = "idle"
        await db.flush()

        return AgentRunResponse(
            status=agent_result.status,
            result=agent_result.data,
            audit_entries=agent_result.audit_entries,
            llm_runtime=claude_client.runtime_info(),
        )
    except Exception as e:
        agent_record.status = "error"
        await db.flush()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution failed: {str(e)}",
        )


@router.delete("/{agent_id}")
async def decommission_agent(
    agent_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    """Decommission an agent (soft delete)."""
    result = await db.execute(select(Agent).where(Agent.id == str(agent_id)))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    agent.status = "decommissioned"
    await db.flush()
    return {"message": f"Agent '{agent.name}' has been decommissioned"}
