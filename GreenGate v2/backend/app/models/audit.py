from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AuditEntry(Base):
    __tablename__ = "audit_entries"
    __table_args__ = (
        Index("ix_audit_org_timestamp", "organisation_id", "timestamp"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    organisation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organisations.id"), nullable=False
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    actor_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # user / agent / system
    actor_id: Mapped[Optional[str]] = mapped_column(String(255))
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    gate_number: Mapped[Optional[int]] = mapped_column(Integer)
    resource_type: Mapped[Optional[str]] = mapped_column(String(100))
    resource_id: Mapped[Optional[str]] = mapped_column(String(255))
    details: Mapped[Optional[dict]] = mapped_column(JSON)
    governance_result: Mapped[Optional[str]] = mapped_column(
        String(20)
    )  # pass / fail / warn
    redacted_fields: Mapped[Optional[list]] = mapped_column(JSON)

    # Relationships
    organisation: Mapped["Organisation"] = relationship(  # noqa: F821
        "Organisation", back_populates="audit_entries"
    )


class CrpDocument(Base):
    __tablename__ = "crp_documents"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    organisation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organisations.id"), nullable=False, index=True
    )
    version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(30), default="draft")  # draft / final / approved
    content: Mapped[Optional[dict]] = mapped_column(JSON)
    ppn006_aligned: Mapped[Optional[bool]] = mapped_column(Boolean)
    sbti_target: Mapped[Optional[dict]] = mapped_column(JSON)
    generated_by: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("agents.id")
    )
    director_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    organisation: Mapped["Organisation"] = relationship(  # noqa: F821
        "Organisation", back_populates="crp_documents"
    )
    agent: Mapped["Agent"] = relationship("Agent")  # noqa: F821


class SecurityCheck(Base):
    __tablename__ = "security_checks"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    organisation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organisations.id"), nullable=False, index=True
    )
    framework: Mapped[str] = mapped_column(
        String(30), nullable=False
    )  # ISO27001 / GDPR / NHS_DSPT
    check_code: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(30), default="not_started"
    )  # not_started / in_progress / pass / fail / na
    evidence_ref: Mapped[Optional[str]] = mapped_column(String(500))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    checked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    organisation: Mapped["Organisation"] = relationship(  # noqa: F821
        "Organisation", back_populates="security_checks"
    )
