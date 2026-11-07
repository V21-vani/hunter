"""ScanLog model — audit log for each source scan/run."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ScanLog(Base):
    __tablename__ = "scan_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    source_scanned: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )  # e.g. 'greenboard:acme', 'lever:acme'
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    jobs_discovered: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    jobs_new: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    jobs_updated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    errors: Mapped[str | None] = mapped_column(Text, nullable=True)
    rate_limited: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), default="running", nullable=False, index=True
    )  # running, completed, failed
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_scan_logs_source_scanned", "source_scanned"),
        Index("ix_scan_logs_status", "status"),
        Index("ix_scan_logs_start_time", "start_time"),
    )

    def __repr__(self) -> str:
        return f"<ScanLog(id={self.id!r}, source_scanned={self.source_scanned!r}, status={self.status!r})>"