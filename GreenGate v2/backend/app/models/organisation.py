from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Organisation(Base):
    __tablename__ = "organisations"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    company_number: Mapped[Optional[str]] = mapped_column(String(20))
    sector: Mapped[Optional[str]] = mapped_column(String(100))
    employee_count: Mapped[Optional[int]] = mapped_column(Integer)
    turnover_band: Mapped[Optional[str]] = mapped_column(String(50))
    country: Mapped[str] = mapped_column(String(10), default="UK")
    reporting_year_start: Mapped[Optional[str]] = mapped_column(String(10))
    current_gate: Mapped[int] = mapped_column(Integer, default=1)
    onboarding_complete: Mapped[bool] = mapped_column(Boolean, default=False)
    frameworks_enrolled: Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    users: Mapped[list] = relationship("User", back_populates="organisation")
    emissions: Mapped[list] = relationship("EmissionsInventory", back_populates="organisation")
    submissions: Mapped[list] = relationship("Submission", back_populates="organisation")
    audit_entries: Mapped[list] = relationship("AuditEntry", back_populates="organisation")
    crp_documents: Mapped[list] = relationship("CrpDocument", back_populates="organisation")
    security_checks: Mapped[list] = relationship("SecurityCheck", back_populates="organisation")
