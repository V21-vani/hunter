"""Company model — employer entity."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    website: Mapped[str | None] = mapped_column(Text, nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    company_size: Mapped[str | None] = mapped_column(String(50), nullable=True)
    headquarters: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    careers_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    verification_status: Mapped[str] = mapped_column(
        String(50), default="unverified", nullable=False, index=True
    )
    is_actively_hiring: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
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
    internships: Mapped[list["Internship"]] = relationship(
        "Internship", back_populates="company", cascade="all, delete-orphan"
    )
    signals: Mapped[list["CompanySignal"]] = relationship(
        "CompanySignal", back_populates="company", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_companies_name", "name"),
        Index("ix_companies_verification_status", "verification_status"),
    )

    def __repr__(self) -> str:
        return f"<Company(id={self.id!r}, name={self.name!r})>"