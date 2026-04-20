from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

import yaml

if TYPE_CHECKING:
    import uuid

    from sqlalchemy.ext.asyncio import AsyncSession

    from app.agents.claude_client import ClaudeClient
    from app.governance.engine import GovernanceEngine
    from app.models.agent import Agent

logger = logging.getLogger("sustaingate.agent")


@dataclass
class AgentResult:
    status: str  # pass / fail / warn
    data: dict = field(default_factory=dict)
    audit_entries: list = field(default_factory=list)


class BaseAgent(ABC):
    """Abstract base class for all SustainGate agents."""

    POLICY_DIR = Path(__file__).parent / "policy_profiles"

    def __init__(
        self,
        agent_record: Agent,
        governance_engine: GovernanceEngine,
        claude_client: ClaudeClient,
        db: AsyncSession,
    ):
        self.record = agent_record
        self.governance = governance_engine
        self.claude = claude_client
        self.db = db
        self._policy: Optional[dict] = None

    def _load_policy(self) -> dict:
        """Load the YAML policy profile for this agent."""
        if self._policy is not None:
            return self._policy

        policy_file = self.POLICY_DIR / f"{self.record.agent_type}.yaml"
        if policy_file.exists():
            with open(policy_file) as f:
                self._policy = yaml.safe_load(f) or {}
        else:
            logger.warning("No policy file found at %s", policy_file)
            self._policy = {}

        return self._policy

    def _get_constraints(self) -> List[str]:
        """Get policy constraints for Claude prompts."""
        policy = self._load_policy()
        return policy.get("constraints", [])

    def _get_allowed_actions(self) -> List[str]:
        """Get the list of allowed actions from policy."""
        policy = self._load_policy()
        return policy.get("allowed_actions", [])

    async def run_action(
        self, org_id: "uuid.UUID", action: str, payload: dict
    ) -> AgentResult:
        """Execute an action through the governance pipeline."""
        # Validate action is allowed
        allowed = self._get_allowed_actions()
        if allowed and action not in allowed:
            return AgentResult(
                status="fail",
                data={"error": f"Action '{action}' not permitted by policy"},
                audit_entries=[],
            )

        # Pre-flight governance check
        gov_result = await self.governance.execute_governed_action(
            agent_id=self.record.id,
            org_id=org_id,
            action=action,
            payload=payload,
            gate_number=self.record.gate_number,
        )

        if gov_result.status == "fail":
            return AgentResult(
                status="fail",
                data={
                    "error": "Governance pre-flight check failed",
                    "violations": gov_result.violations,
                },
                audit_entries=gov_result.audit_entries,
            )

        # Execute the agent-specific logic
        try:
            result_data = await self._execute(org_id, action, gov_result.payload)
        except Exception as e:
            logger.error("Agent execution failed: %s", e, exc_info=True)
            return AgentResult(
                status="fail",
                data={"error": str(e)},
                audit_entries=gov_result.audit_entries,
            )

        return AgentResult(
            status=gov_result.status,
            data=result_data,
            audit_entries=gov_result.audit_entries,
        )

    @abstractmethod
    async def _execute(
        self, org_id: "uuid.UUID", action: str, payload: dict
    ) -> dict:
        """Implement the agent-specific logic. Must return a dict of results."""
        ...
