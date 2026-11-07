"""Internship model — detailed internship record."""

import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Internship(Base):
    __tablename__ = "internships"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    role_title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    role_category: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    skills: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    stipend_min: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    stipend_max: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    incentives: Mapped[str | None] = mapped_column(Text, nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    remote_status: Mapped[str] = mapped_column(
        String(50), default="onsite", nullable=False, index=True
    )
    india_eligible: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, index=True
    )
    duration_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    weekly_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)
    experience_requirements: Mapped[str | None] = mapped_column(String(255), nullable=True)
    education_requirements: Mapped[str | None] = mapped_column(String(255), nullable=True)
    application_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    original_posting_date: Mapped[date | None] = mapped_column(nullable=True)
    deadline: Mapped[date | None] = mapped_column(nullable=True)
    first_discovered_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_verified_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(50), default="discovered", nullable=False, index=True
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
    company: Mapped["Company | None"] = relationship(
        "Company", back_populates="internships"
    )
    sources: Mapped[list["Source"]] = relationship(
        "Source",
        secondary="internship_sources",
        back_populates="internships",
    )
    verifications: Mapped[list["Verification"]] = relationship(
        "Verification", back_populates="internship", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_internships_company_id", "company_id"),
        Index("ix_internships_status_remote_india", "status", "remote_status", "india_eligible"),
        Index("ix_internships_role_category", "role_category"),
        Index("ix_internships_first_discovered", "first_discovered_date"),
    )

    def __repr__(self) -> str:
        return f"<Internship(id={self.id!r}, role_title={self.role_title!r}, company_id={self.company_id!r})>"