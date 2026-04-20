from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class EmissionsInventory(Base):
    __tablename__ = "emissions_inventory"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    organisation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organisations.id"), nullable=False, index=True
    )
    reporting_year: Mapped[int] = mapped_column(Integer, nullable=False)
    scope: Mapped[int] = mapped_column(Integer, nullable=False)  # 1, 2, 3
    category: Mapped[str] = mapped_column(String(255), nullable=False)
    source: Mapped[Optional[str]] = mapped_column(String(255))
    activity_data: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 6))
    activity_unit: Mapped[Optional[str]] = mapped_column(String(50))
    emission_factor: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 8))
    emission_factor_source: Mapped[Optional[str]] = mapped_column(String(255))
    co2e_tonnes: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 6))
    confidence_tier: Mapped[Optional[str]] = mapped_column(
        String(20)
    )  # high / medium / low / estimated
    data_source: Mapped[Optional[str]] = mapped_column(String(255))
    evidence_ref: Mapped[Optional[str]] = mapped_column(String(500))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    organisation: Mapped["Organisation"] = relationship(  # noqa: F821
        "Organisation", back_populates="emissions"
    )
