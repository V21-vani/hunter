"""Verification model — staged verification records for internships.

Each internship goes through verification levels 1-5:
  level_1: EMPLOYER VERIFIED
  level_2: EMPLOYER LISTING, DETAILS INCOMPLETE
  level_3: AGGREGATOR ONLY
  level_4: SOCIAL LEAD — NOT VERIFIED
  level_5: EXPIRED / REJECTED
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Verification(Base):
    __tablename__ = "verifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    internship_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("internships.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    level: Mapped[str] = mapped_column(
        String(20), nullable=False, default="level_1", index=True
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending", index=True
    )
    evidence: Mapped[dict | None] = mapped_column(
        JSONB(astext_type=sa.Text()), nullable=True
    )
    stipend_confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    india_eligible_confirmed: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    remote_eligible_confirmed: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    stipend_amount: Mapped[float | None] = mapped_column(
        nullable=True
    )
    stipend_currency: Mapped[str] = mapped_column(
        String(10), default="INR", nullable=False
    )
    stipend_type: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )  # fixed, incentive, commission, hourly
    application_url_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    remote_eligibility_established: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    company_identity_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    role_matched: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    company_identity_matched: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    original_publication_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    verified_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    verification_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationship
    internship: Mapped["Internship"] = relationship(
        "Internship", back_populates="verifications"
    )

    __table_args__ = (
        Index("ix_verifications_internship_id", "internship_id"),
        Index("ix_verifications_level_status", "level", "status"),
    )

    def __repr__(self) -> str:
        return f"<Verification(id={self.id!r}, internship_id={self.internship_id!r}, level={self.level!r}, status={self.status!r})>"