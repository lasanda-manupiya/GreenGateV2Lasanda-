from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession

from app.governance.audit_log import AuditLogger
from app.governance.redaction import RedactionEngine
from app.governance.rules import RuleEvaluator


@dataclass
class GovernanceResult:
    status: str  # pass / fail / warn
    payload: dict = field(default_factory=dict)
    audit_entries: list = field(default_factory=list)
    violations: list = field(default_factory=list)


class GovernanceEngine:
    """Central governance engine that enforces rules, applies redaction, and logs audit entries."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.rule_evaluator = RuleEvaluator(db_session)
        self.redaction_engine = RedactionEngine()
        self.audit_logger = AuditLogger(db_session)

    async def execute_governed_action(
        self,
        agent_id: uuid.UUID,
        org_id: uuid.UUID,
        action: str,
        payload: dict,
        gate_number: int,
    ) -> GovernanceResult:
        """Execute an action through the governance pipeline."""
        audit_entries = []
        violations = []

        # 1. Pre-flight check: load and evaluate applicable rules
        rules = await self.rule_evaluator.get_rules(gate_number, action, payload)
        eval_result = await self.rule_evaluator.evaluate(rules, payload, phase="pre")

        if eval_result.has_critical_failure:
            # Log the blocked action
            entry = await self.audit_logger.log(
                actor_type="agent",
                actor_id=str(agent_id),
                org_id=org_id,
                action=action,
                gate_number=gate_number,
                resource_type="governance_check",
                resource_id=str(uuid.uuid4()),
                details={
                    "phase": "pre-flight",
                    "failures": [
                        {"rule_code": r.rule_code, "message": r.message}
                        for r in eval_result.results
                        if not r.passed
                    ],
                },
                governance_result="fail",
                redacted_fields=[],
            )
            audit_entries.append(str(entry.id))
            violations = [
                {"rule_code": r.rule_code, "message": r.message}
                for r in eval_result.results
                if not r.passed
            ]

            return GovernanceResult(
                status="fail",
                payload=payload,
                audit_entries=audit_entries,
                violations=violations,
            )

        # 2. Apply redaction to payload
        redacted_payload = self.redaction_engine.redact(payload)
        redacted_fields = self.redaction_engine.last_redacted

        # 3. Determine overall status
        status = "warn" if eval_result.warnings else "pass"

        # 4. Log the governance result
        entry = await self.audit_logger.log(
            actor_type="agent",
            actor_id=str(agent_id),
            org_id=org_id,
            action=action,
            gate_number=gate_number,
            resource_type="governance_check",
            resource_id=str(uuid.uuid4()),
            details={
                "phase": "pre-flight",
                "rule_count": len(rules),
                "warnings": eval_result.warnings,
                "redacted_field_count": len(redacted_fields),
            },
            governance_result=status,
            redacted_fields=redacted_fields,
        )
        audit_entries.append(str(entry.id))

        return GovernanceResult(
            status=status,
            payload=redacted_payload,
            audit_entries=audit_entries,
            violations=[
                {"rule_code": r.rule_code, "message": r.message}
                for r in eval_result.results
                if not r.passed
            ],
        )
