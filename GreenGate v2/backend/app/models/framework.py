from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Framework(Base):
    __tablename__ = "frameworks"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[Optional[str]] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(Text)
    jurisdiction: Mapped[Optional[str]] = mapped_column(String(100))
    gate_number: Mapped[Optional[int]] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    rules: Mapped[List["Rule"]] = relationship("Rule", back_populates="framework")


class Rule(Base):
    __tablename__ = "rules"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    framework_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("frameworks.id"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    rule_type: Mapped[str] = mapped_column(
        String(30), nullable=False
    )  # validation / redaction / permission / threshold
    severity: Mapped[str] = mapped_column(
        String(20), nullable=False, default="warning"
    )  # blocker / warning / info
    check_expression: Mapped[Optional[dict]] = mapped_column(JSON)
    effective_date: Mapped[Optional[date]] = mapped_column(Date)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    framework: Mapped["Framework"] = relationship("Framework", back_populates="rules")
