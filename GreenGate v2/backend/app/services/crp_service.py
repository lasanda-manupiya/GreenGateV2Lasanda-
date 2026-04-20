from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import CrpDocument


async def create_crp_document(
    db: AsyncSession,
    organisation_id: uuid.UUID,
    content: dict,
    agent_id: Optional[uuid.UUID] = None,
    ppn006_aligned: bool = False,
    sbti_target: Optional[dict] = None,
) -> CrpDocument:
    # Get latest version number
    result = await db.execute(
        select(CrpDocument.version)
        .where(CrpDocument.organisation_id == organisation_id)
        .order_by(CrpDocument.version.desc())
        .limit(1)
    )
    latest_version = result.scalar()
    next_version = (latest_version or 0) + 1

    crp = CrpDocument(
        organisation_id=organisation_id,
        version=next_version,
        content=content,
        generated_by=agent_id,
        ppn006_aligned=ppn006_aligned,
        sbti_target=sbti_target,
    )
    db.add(crp)
    await db.flush()
    return crp


async def get_latest_crp(
    db: AsyncSession, organisation_id: uuid.UUID
) -> Optional[CrpDocument]:
    result = await db.execute(
        select(CrpDocument)
        .where(CrpDocument.organisation_id == organisation_id)
        .order_by(CrpDocument.version.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def approve_crp(
    db: AsyncSession, crp_id: uuid.UUID
) -> Optional[CrpDocument]:
    result = await db.execute(select(CrpDocument).where(CrpDocument.id == crp_id))
    crp = result.scalar_one_or_none()
    if crp:
        crp.director_approved = True
        crp.status = "approved"
        await db.flush()
    return crp
