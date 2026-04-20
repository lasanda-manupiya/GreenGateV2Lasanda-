from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    organisation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organisations.id"), nullable=False, index=True
    )
    gate_number: Mapped[int] = mapped_column(Integer, nullable=False)
    framework_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("frameworks.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(30), default="draft"
    )  # draft / submitted / under_review / approved / rejected
    submitted_by: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id")
    )
    content: Mapped[Optional[dict]] = mapped_column(JSON)
    score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    feedback: Mapped[Optional[str]] = mapped_column(Text)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    organisation: Mapped["Organisation"] = relationship(  # noqa: F821
        "Organisation", back_populates="submissions"
    )
    framework: Mapped["Framework"] = relationship("Framework")  # noqa: F821
    submitter: Mapped["User"] = relationship("User")  # noqa: F821
