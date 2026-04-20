from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.framework import Rule


@dataclass
class RuleResult:
    rule_id: str
    rule_code: str
    passed: bool
    message: str


@dataclass
class EvaluationResult:
    has_critical_failure: bool = False
    results: List[RuleResult] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class RuleEvaluator:
    """Evaluates governance rules against action payloads."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_rules(
        self,
        gate_number: int,
        action: str,
        payload: Optional[dict] = None,
    ) -> List[Rule]:
        """Load active rules applicable to this gate, action, and payload.

        Framework-specific submission rules only fire when the action explicitly
        targets that framework (via `payload['framework_id']`). Action/gate
        matching via `check_expression` still works for cross-framework rules.
        """
        result = await self.db.execute(
            select(Rule)
            .where(Rule.is_active.is_(True))
            .options(selectinload(Rule.framework))
        )
        all_rules = result.scalars().all()

        payload = payload or {}
        target_framework_id = payload.get("framework_id")

        applicable = []
        for rule in all_rules:
            expr = rule.check_expression or {}

            # 1. Explicit action match in check_expression
            if expr.get("action") == action:
                applicable.append(rule)
                continue

            # 2. Explicit gate match in check_expression
            if expr.get("gate") == gate_number:
                applicable.append(rule)
                continue

            # 3. Framework-submission rule: only apply when the action is
            #    actually submitting to / operating on that framework.
            if (
                rule.framework
                and rule.framework.gate_number == gate_number
                and target_framework_id
                and str(rule.framework_id) == str(target_framework_id)
            ):
                applicable.append(rule)

        return applicable

    async def evaluate(
        self, rules: List[Rule], payload: dict, phase: str = "pre"
    ) -> EvaluationResult:
        """Evaluate rules against the payload."""
        results: List[RuleResult] = []
        warnings: List[str] = []
        has_critical = False

        for rule in rules:
            passed, message = self._check_rule(rule, payload)
            result = RuleResult(
                rule_id=str(rule.id),
                rule_code=rule.code,
                passed=passed,
                message=message,
            )
            results.append(result)

            if not passed:
                if rule.severity == "blocker":
                    has_critical = True
                elif rule.severity == "warning":
                    warnings.append(f"[{rule.code}] {message}")

        return EvaluationResult(
            has_critical_failure=has_critical,
            results=results,
            warnings=warnings,
        )

    def _check_rule(self, rule: Rule, payload: dict) -> Tuple[bool, str]:
        """Evaluate a single rule against payload data. Returns (passed, message)."""
        expr = rule.check_expression or {}
        check_type = expr.get("check_type", "")

        if check_type == "required_fields":
            return self._check_required_fields(expr, payload)
        elif check_type == "numeric_range":
            return self._check_numeric_range(expr, payload)
        elif check_type == "confidence_tier":
            return self._check_confidence_tier(expr, payload)
        elif check_type == "data_source_documented":
            return self._check_data_source(expr, payload)
        elif check_type == "emission_factor_valid":
            return self._check_emission_factor(expr, payload)
        elif check_type == "threshold":
            return self._check_threshold(expr, payload)
        elif check_type == "field_present":
            return self._check_field_present(expr, payload)
        else:
            # Unknown check type passes by default with a warning
            return True, f"Unrecognised check type '{check_type}' - skipped"

    def _check_required_fields(
        self, expr: dict, payload: dict
    ) -> Tuple[bool, str]:
        required = expr.get("fields", [])
        missing = [f for f in required if f not in payload or payload[f] is None]
        if missing:
            return False, f"Missing required fields: {', '.join(missing)}"
        return True, "All required fields present"

    def _check_numeric_range(
        self, expr: dict, payload: dict
    ) -> Tuple[bool, str]:
        field_name = expr.get("field", "")
        min_val = expr.get("min")
        max_val = expr.get("max")
        value = payload.get(field_name)
        if value is None:
            return False, f"Field '{field_name}' not provided for range check"
        try:
            num_value = float(value)
        except (TypeError, ValueError):
            return False, f"Field '{field_name}' is not a valid number"
        if min_val is not None and num_value < min_val:
            return False, f"Field '{field_name}' value {num_value} below minimum {min_val}"
        if max_val is not None and num_value > max_val:
            return False, f"Field '{field_name}' value {num_value} above maximum {max_val}"
        return True, f"Field '{field_name}' value {num_value} within valid range"

    def _check_confidence_tier(
        self, expr: dict, payload: dict
    ) -> Tuple[bool, str]:
        valid_tiers = {"high", "medium", "low", "estimated"}
        tier = payload.get("confidence_tier")
        if not tier:
            return False, "Confidence tier not assigned"
        if tier.lower() not in valid_tiers:
            return False, f"Invalid confidence tier '{tier}'"
        return True, f"Confidence tier '{tier}' assigned"

    def _check_data_source(
        self, expr: dict, payload: dict
    ) -> Tuple[bool, str]:
        source = payload.get("data_source") or payload.get("emission_factor_source")
        if not source:
            return False, "Data source not documented"
        return True, f"Data source documented: {source}"

    def _check_emission_factor(
        self, expr: dict, payload: dict
    ) -> Tuple[bool, str]:
        ef = payload.get("emission_factor")
        if ef is None:
            return False, "No emission factor provided"
        try:
            ef_val = float(ef)
        except (TypeError, ValueError):
            return False, "Emission factor is not a valid number"
        if ef_val <= 0:
            return False, "Emission factor must be positive"
        source = payload.get("emission_factor_source", "")
        if not source:
            return False, "Emission factor source not documented"
        return True, f"Emission factor {ef_val} from {source} is valid"

    def _check_threshold(
        self, expr: dict, payload: dict
    ) -> Tuple[bool, str]:
        field_name = expr.get("field", "")
        threshold = expr.get("threshold", 0)
        operator = expr.get("operator", "<=")
        value = payload.get(field_name)
        if value is None:
            return True, f"Field '{field_name}' not present, threshold check skipped"
        try:
            num_value = float(value)
        except (TypeError, ValueError):
            return False, f"Field '{field_name}' is not a valid number"
        if operator == "<=" and num_value > threshold:
            return False, f"Field '{field_name}' value {num_value} exceeds threshold {threshold}"
        if operator == ">=" and num_value < threshold:
            return False, f"Field '{field_name}' value {num_value} below threshold {threshold}"
        return True, f"Field '{field_name}' passes threshold check"

    def _check_field_present(
        self, expr: dict, payload: dict
    ) -> Tuple[bool, str]:
        field_name = expr.get("field", "")
        if field_name not in payload or payload[field_name] is None:
            return False, f"Required field '{field_name}' is not present"
        return True, f"Field '{field_name}' is present"
