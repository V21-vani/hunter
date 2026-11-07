"""Source model — original discovery source for an internship."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    source_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # e.g. 'greenhouse', 'lever', 'company_page', 'linkedin_post'
    original_source_url: Mapped[str] = mapped_column(Text, nullable=False)
    platform: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    author_company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    original_publication_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    discovery_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    evidence_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    internships: Mapped[list["Internship"]] = relationship(
        "Internship",
        secondary="internship_sources",
        back_populates="sources",
    )

    __table_args__ = (
        Index("ix_sources_source_type_platform", "source_type", "platform"),
        Index("ix_sources_discovery_timestamp", "discovery_timestamp"),
    )

    def __repr__(self) -> str:
        return f"<Source(id={self.id!r}, source_type={self.source_type!r}, platform={self.platform!r})>"