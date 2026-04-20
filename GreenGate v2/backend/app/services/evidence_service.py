from __future__ import annotations

import csv
import io
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.emissions import EmissionsInventory
from app.models.audit import AuditEntry, CrpDocument, SecurityCheck
from app.models.submission import Submission


async def generate_evidence_pack(
    db: AsyncSession, org_id: uuid.UUID
) -> Path:
    """Generate a ZIP evidence pack with CSV exports for an organisation."""
    storage_path = Path(settings.STORAGE_PATH)
    storage_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    zip_filename = f"evidence_pack_{org_id}_{timestamp}.zip"
    zip_path = storage_path / zip_filename

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        # Emissions inventory CSV
        emissions_csv = await _export_emissions_csv(db, org_id)
        zf.writestr("emissions_inventory.csv", emissions_csv)

        # Audit trail CSV
        audit_csv = await _export_audit_csv(db, org_id)
        zf.writestr("audit_trail.csv", audit_csv)

        # Submissions CSV
        submissions_csv = await _export_submissions_csv(db, org_id)
        zf.writestr("submissions.csv", submissions_csv)

        # Security checks CSV
        security_csv = await _export_security_csv(db, org_id)
        zf.writestr("security_checks.csv", security_csv)

        # Manifest
        manifest = _generate_manifest(org_id, timestamp)
        zf.writestr("MANIFEST.txt", manifest)

    zip_path.write_bytes(zip_buffer.getvalue())
    return zip_path


async def _export_emissions_csv(db: AsyncSession, org_id: uuid.UUID) -> str:
    result = await db.execute(
        select(EmissionsInventory)
        .where(EmissionsInventory.organisation_id == org_id)
        .order_by(EmissionsInventory.reporting_year, EmissionsInventory.scope)
    )
    entries = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "id", "reporting_year", "scope", "category", "source",
        "activity_data", "activity_unit", "emission_factor",
        "emission_factor_source", "co2e_tonnes", "confidence_tier",
        "data_source", "evidence_ref", "notes",
    ])
    for e in entries:
        writer.writerow([
            str(e.id), e.reporting_year, e.scope, e.category, e.source,
            e.activity_data, e.activity_unit, e.emission_factor,
            e.emission_factor_source, e.co2e_tonnes, e.confidence_tier,
            e.data_source, e.evidence_ref, e.notes,
        ])
    return output.getvalue()


async def _export_audit_csv(db: AsyncSession, org_id: uuid.UUID) -> str:
    result = await db.execute(
        select(AuditEntry)
        .where(AuditEntry.organisation_id == org_id)
        .order_by(AuditEntry.timestamp.desc())
    )
    entries = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "id", "timestamp", "actor_type", "actor_id", "action",
        "gate_number", "resource_type", "resource_id",
        "governance_result", "redacted_fields",
    ])
    for e in entries:
        writer.writerow([
            str(e.id), e.timestamp, e.actor_type, e.actor_id, e.action,
            e.gate_number, e.resource_type, e.resource_id,
            e.governance_result, e.redacted_fields,
        ])
    return output.getvalue()


async def _export_submissions_csv(db: AsyncSession, org_id: uuid.UUID) -> str:
    result = await db.execute(
        select(Submission)
        .where(Submission.organisation_id == org_id)
        .order_by(Submission.created_at.desc())
    )
    entries = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "id", "gate_number", "framework_id", "status", "submitted_by",
        "score", "feedback", "submitted_at", "reviewed_at", "created_at",
    ])
    for e in entries:
        writer.writerow([
            str(e.id), e.gate_number, str(e.framework_id), e.status,
            str(e.submitted_by) if e.submitted_by else "", e.score,
            e.feedback, e.submitted_at, e.reviewed_at, e.created_at,
        ])
    return output.getvalue()


async def _export_security_csv(db: AsyncSession, org_id: uuid.UUID) -> str:
    result = await db.execute(
        select(SecurityCheck)
        .where(SecurityCheck.organisation_id == org_id)
        .order_by(SecurityCheck.framework, SecurityCheck.check_code)
    )
    entries = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "id", "framework", "check_code", "description", "status",
        "evidence_ref", "notes", "checked_at",
    ])
    for e in entries:
        writer.writerow([
            str(e.id), e.framework, e.check_code, e.description,
            e.status, e.evidence_ref, e.notes, e.checked_at,
        ])
    return output.getvalue()


def _generate_manifest(org_id: uuid.UUID, timestamp: str) -> str:
    return f"""SustainGate Evidence Pack
========================
Organisation ID: {org_id}
Generated:       {timestamp}
Format:          CSV (UTF-8)

Contents:
  - emissions_inventory.csv  : Full GHG emissions inventory
  - audit_trail.csv          : Governance audit trail
  - submissions.csv          : Gate submissions and reviews
  - security_checks.csv      : Security compliance checks

This evidence pack was generated automatically by SustainGate.
All data has been processed through the governance engine with
redaction applied where applicable.
"""
