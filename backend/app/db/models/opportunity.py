"""Opportunity model — canonical internship record."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Opportunity(Base):
    __tablename__ = "opportunities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    source: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    source_id: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    employer_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    company_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_raw: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_remote: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_paid: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    stipend_min: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    stipend_max: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    stipend_currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    duration_min_months: Mapped[int | None] = mapped_column(nullable=True)
    duration_max_months: Mapped[int | None] = mapped_column(nullable=True)
    eligibility: Mapped[str | None] = mapped_column(Text, nullable=True)
    application_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    application_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), index=True, default="discovered", nullable=False
    )
    verification_status: Mapped[str] = mapped_column(
        String(50), default="pending", nullable=False
    )
    verification_evidence: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    rank_score: Mapped[float | None] = mapped_column(Numeric(10, 4), index=True, nullable=True)
    rank_factors: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index("uq_opportunity_source_source_id", "source", "source_id", unique=True),
        Index("ix_opportunity_status_remote_paid", "status", "is_remote", "is_paid"),
    )

    def __repr__(self) -> str:
        return f"<Opportunity(source={self.source!r}, source_id={self.source_id!r}, title={self.title!r})>"