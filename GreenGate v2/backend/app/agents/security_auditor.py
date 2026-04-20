from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base_agent import BaseAgent
from app.models.audit import SecurityCheck
from app.models.organisation import Organisation

logger = logging.getLogger("sustaingate.agent.security_auditor")

# ISO 27001 key controls for baseline check
ISO27001_CONTROLS = [
    {"code": "A.5.1", "description": "Information security policies", "category": "Governance"},
    {"code": "A.6.1", "description": "Organisation of information security", "category": "Governance"},
    {"code": "A.7.1", "description": "Human resource security - prior to employment", "category": "People"},
    {"code": "A.8.1", "description": "Asset management - responsibility for assets", "category": "Assets"},
    {"code": "A.9.1", "description": "Access control policy", "category": "Access"},
    {"code": "A.9.2", "description": "User access management", "category": "Access"},
    {"code": "A.9.4", "description": "System and application access control", "category": "Access"},
    {"code": "A.10.1", "description": "Cryptographic controls", "category": "Cryptography"},
    {"code": "A.11.1", "description": "Physical security perimeter", "category": "Physical"},
    {"code": "A.12.1", "description": "Operational procedures and responsibilities", "category": "Operations"},
    {"code": "A.12.2", "description": "Protection from malware", "category": "Operations"},
    {"code": "A.12.3", "description": "Backup", "category": "Operations"},
    {"code": "A.12.4", "description": "Logging and monitoring", "category": "Operations"},
    {"code": "A.13.1", "description": "Network security management", "category": "Communications"},
    {"code": "A.14.1", "description": "Security requirements of information systems", "category": "Development"},
    {"code": "A.16.1", "description": "Management of information security incidents", "category": "Incident"},
    {"code": "A.17.1", "description": "Information security aspects of business continuity", "category": "Continuity"},
    {"code": "A.18.1", "description": "Compliance with legal and regulatory requirements", "category": "Compliance"},
]

# GDPR Article 5 principles
GDPR_CHECKS = [
    {"code": "GDPR-5.1a", "description": "Lawfulness, fairness, and transparency of processing"},
    {"code": "GDPR-5.1b", "description": "Purpose limitation - collected for specified purposes"},
    {"code": "GDPR-5.1c", "description": "Data minimisation - adequate, relevant, and limited"},
    {"code": "GDPR-5.1d", "description": "Accuracy - kept up to date, rectified without delay"},
    {"code": "GDPR-5.1e", "description": "Storage limitation - kept no longer than necessary"},
    {"code": "GDPR-5.1f", "description": "Integrity and confidentiality (security)"},
    {"code": "GDPR-5.2", "description": "Accountability - controller responsible and able to demonstrate compliance"},
    {"code": "GDPR-DPO", "description": "Data Protection Officer appointed where required"},
    {"code": "GDPR-DPIA", "description": "Data Protection Impact Assessments for high-risk processing"},
    {"code": "GDPR-SAR", "description": "Subject Access Request process in place"},
    {"code": "GDPR-BREACH", "description": "Breach notification procedure (72-hour reporting)"},
    {"code": "GDPR-INTL", "description": "International transfer safeguards (post-Brexit adequacy)"},
]

# NHS DSPT standards
NHS_DSPT_CHECKS = [
    {"code": "DSPT-1.1", "description": "Senior leadership responsibility for data security"},
    {"code": "DSPT-1.2", "description": "Data security and protection training programme"},
    {"code": "DSPT-2.1", "description": "Understanding personal data held and lawful basis"},
    {"code": "DSPT-2.2", "description": "Data flow mapping maintained and reviewed"},
    {"code": "DSPT-3.1", "description": "Staff data security training completed annually"},
    {"code": "DSPT-3.2", "description": "Phishing awareness training delivered"},
    {"code": "DSPT-4.1", "description": "Managing data access - role-based permissions"},
    {"code": "DSPT-5.1", "description": "Process reviews for identifying and improving security"},
    {"code": "DSPT-6.1", "description": "Responding to incidents - documented plan"},
    {"code": "DSPT-6.2", "description": "Incident reporting to DHSC/ICO when required"},
    {"code": "DSPT-7.1", "description": "Business continuity plan including data recovery"},
    {"code": "DSPT-8.1", "description": "Unsupported systems identified and risk managed"},
    {"code": "DSPT-9.1", "description": "IT asset management and disposal procedures"},
    {"code": "DSPT-10.1", "description": "Networking and security - firewalls, patching, monitoring"},
]


class SecurityAuditor(BaseAgent):
    """Gate 6 agent: Security and data governance assessment."""

    def __init__(self, agent_record, governance_engine, claude_client, db: AsyncSession):
        super().__init__(agent_record, governance_engine, claude_client, db)

    async def _execute(self, org_id: uuid.UUID, action: str, payload: dict) -> dict:
        if action == "run_baseline_check":
            return await self._run_baseline_check(org_id, payload)
        elif action == "assess_gdpr":
            return await self._assess_gdpr(org_id, payload)
        elif action == "check_nhs_dspt":
            return await self._check_nhs_dspt(org_id, payload)
        elif action == "generate_remediation":
            return await self._generate_remediation(org_id, payload)
        else:
            raise ValueError(f"Unsupported action: {action}")

    async def _run_baseline_check(self, org_id: uuid.UUID, payload: dict) -> dict:
        """Evaluate org against ISO 27001 key controls."""
        now = datetime.now(timezone.utc)
        results = []

        for control in ISO27001_CONTROLS:
            # Check if a security check already exists
            existing = await self.db.execute(
                select(SecurityCheck).where(
                    SecurityCheck.organisation_id == org_id,
                    SecurityCheck.framework == "ISO27001",
                    SecurityCheck.check_code == control["code"],
                )
            )
            check = existing.scalar_one_or_none()

            if not check:
                check = SecurityCheck(
                    organisation_id=org_id,
                    framework="ISO27001",
                    check_code=control["code"],
                    description=control["description"],
                    status="not_started",
                    created_at=now,
                )
                self.db.add(check)

            results.append({
                "code": control["code"],
                "description": control["description"],
                "category": control["category"],
                "status": check.status,
            })

        await self.db.flush()

        # Calculate summary
        total = len(results)
        passed = sum(1 for r in results if r["status"] == "pass")
        failed = sum(1 for r in results if r["status"] == "fail")
        not_started = sum(1 for r in results if r["status"] == "not_started")

        return {
            "framework": "ISO 27001",
            "total_controls": total,
            "passed": passed,
            "failed": failed,
            "not_started": not_started,
            "in_progress": total - passed - failed - not_started,
            "compliance_pct": round((passed / total) * 100, 1) if total else 0,
            "controls": results,
        }

    async def _assess_gdpr(self, org_id: uuid.UUID, payload: dict) -> dict:
        """Run GDPR compliance assessment."""
        now = datetime.now(timezone.utc)
        results = []

        for check_def in GDPR_CHECKS:
            existing = await self.db.execute(
                select(SecurityCheck).where(
                    SecurityCheck.organisation_id == org_id,
                    SecurityCheck.framework == "GDPR",
                    SecurityCheck.check_code == check_def["code"],
                )
            )
            check = existing.scalar_one_or_none()

            if not check:
                check = SecurityCheck(
                    organisation_id=org_id,
                    framework="GDPR",
                    check_code=check_def["code"],
                    description=check_def["description"],
                    status="not_started",
                    created_at=now,
                )
                self.db.add(check)

            results.append({
                "code": check_def["code"],
                "description": check_def["description"],
                "status": check.status,
            })

        await self.db.flush()

        total = len(results)
        passed = sum(1 for r in results if r["status"] == "pass")

        return {
            "framework": "GDPR",
            "total_checks": total,
            "passed": passed,
            "compliance_pct": round((passed / total) * 100, 1) if total else 0,
            "checks": results,
        }

    async def _check_nhs_dspt(self, org_id: uuid.UUID, payload: dict) -> dict:
        """Run NHS Data Security and Protection Toolkit assessment."""
        now = datetime.now(timezone.utc)
        results = []

        for check_def in NHS_DSPT_CHECKS:
            existing = await self.db.execute(
                select(SecurityCheck).where(
                    SecurityCheck.organisation_id == org_id,
                    SecurityCheck.framework == "NHS_DSPT",
                    SecurityCheck.check_code == check_def["code"],
                )
            )
            check = existing.scalar_one_or_none()

            if not check:
                check = SecurityCheck(
                    organisation_id=org_id,
                    framework="NHS_DSPT",
                    check_code=check_def["code"],
                    description=check_def["description"],
                    status="not_started",
                    created_at=now,
                )
                self.db.add(check)

            results.append({
                "code": check_def["code"],
                "description": check_def["description"],
                "status": check.status,
            })

        await self.db.flush()

        total = len(results)
        passed = sum(1 for r in results if r["status"] == "pass")

        return {
            "framework": "NHS DSPT",
            "total_checks": total,
            "passed": passed,
            "compliance_pct": round((passed / total) * 100, 1) if total else 0,
            "checks": results,
        }

    async def _generate_remediation(self, org_id: uuid.UUID, payload: dict) -> dict:
        """Use Claude to generate remediation recommendations based on failed checks."""
        # Fetch all failed/not_started security checks
        result = await self.db.execute(
            select(SecurityCheck).where(
                SecurityCheck.organisation_id == org_id,
                SecurityCheck.status.in_(["fail", "not_started"]),
            )
        )
        checks = list(result.scalars().all())

        if not checks:
            return {
                "message": "No failed or outstanding security checks found.",
                "remediation_plan": [],
            }

        # Build summary for Claude
        check_summary = []
        for c in checks:
            check_summary.append(
                f"- [{c.framework}] {c.check_code}: {c.description} (status: {c.status})"
            )
        summary_text = "\n".join(check_summary)

        prompt = (
            f"Generate a prioritised remediation plan for the following outstanding "
            f"security and compliance checks:\n\n{summary_text}\n\n"
            f"For each item, provide: area, finding, severity (high/medium/low), "
            f"specific recommendation, effort level, and suggested timeline.\n"
            f"Return as JSON with a remediation_plan array and priority_order summary."
        )

        constraints = self._get_constraints()
        response = await self.claude.complete(
            system_prompt=(
                "You are a cybersecurity and data protection consultant "
                "specialising in ISO 27001, GDPR, and NHS DSPT compliance. "
                "Generate practical, actionable remediation recommendations."
            ),
            user_message=prompt,
            policy_constraints=constraints,
        )

        try:
            remediation = json.loads(response)
        except json.JSONDecodeError:
            remediation = {"raw_response": response}

        return {
            "outstanding_checks": len(checks),
            "frameworks_covered": list(set(c.framework for c in checks)),
            "remediation": remediation,
        }
