"""InternshipSource association table — links internships to their discovery sources."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class InternshipSource(Base):
    __tablename__ = "internship_sources"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    internship_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("internships.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    relationship_type: Mapped[str] = mapped_column(
        String(50), default="duplicate", nullable=False
    )  # 'original', 'duplicate', 'cross_post'
    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("uq_internship_source", "internship_id", "source_id", unique=True),
        Index("ix_internship_sources_internship_id", "internship_id"),
        Index("ix_internship_sources_source_id", "source_id"),
    )

    def __repr__(self) -> str:
        return f"<InternshipSource(internship_id={self.internship_id!r}, source_id={self.source_id!r})>"