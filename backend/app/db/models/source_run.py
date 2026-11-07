"""Source run model — tracks each adapter execution."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SourceRun(Base):
    __tablename__ = "source_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    source: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    adapter_name: Mapped[str] = mapped_column(String(100), nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="running", nullable=False)
    opportunities_found: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    opportunities_new: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    opportunities_updated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (Index("ix_source_runs_source_started", "source", "started_at"),)

    def __repr__(self) -> str:
        return f"<SourceRun(source={self.source!r}, status={self.status!r})>"