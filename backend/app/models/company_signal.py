"""CompanySignal model — hiring signals detected for a company."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CompanySignal(Base):
    __tablename__ = "company_signals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    signal_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # e.g. 'hiring_spike', 'new_role_posted', 'founder_announcement'
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    publication_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    signal_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    has_opening: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )  # Whether a corresponding official opening exists
    confidence_score: Mapped[float] = mapped_column(
        default=0.5, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    company: Mapped["Company"] = relationship(
        "Company", back_populates="signals"
    )

    __table_args__ = (
        Index("ix_company_signals_company_id", "company_id"),
        Index("ix_company_signals_signal_type", "signal_type"),
        Index("ix_company_signals_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<CompanySignal(id={self.id!r}, company_id={self.company_id!r}, signal_type={self.signal_type!r})>"