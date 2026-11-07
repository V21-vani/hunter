"""Verification model — employer/opening verification record."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
    employer_verification_status: Mapped[str] = mapped_column(
        String(50), default="pending", nullable=False, index=True
    )  # pending, verified, rejected, expired
    official_careers_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    ats_confirmation: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    stipend_confirmation: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    remote_eligibility_confirmation: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    verification_evidence: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    last_checked: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    internship: Mapped["Internship"] = relationship(
        "Internship", back_populates="verifications"
    )

    __table_args__ = (
        Index("ix_verifications_internship_id", "internship_id"),
        Index("ix_verifications_employer_status", "employer_verification_status"),
        Index("ix_verifications_last_checked", "last_checked"),
    )

    def __repr__(self) -> str:
        return f"<Verification(id={self.id!r}, internship_id={self.internship_id!r}, status={self.employer_verification_status!r})>"