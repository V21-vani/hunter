"""SocialSignal model — a discovery signal from public social platforms.

A social signal is a DISCOVERY SIGNAL, not proof of an active internship.
It must be matched against an official careers page or employer-owned
application route.  If no official opening can be confirmed, the signal
is marked SOCIAL LEAD — NOT VERIFIED.
"""

import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import Boolean, DateTime, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SocialSignal(Base):
    __tablename__ = "social_signals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    platform: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    post_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    author_role: Mapped[str | None] = mapped_column(String(255), nullable=True)
    company: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    post_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    post_url: Mapped[str | None] = mapped_column(Text, nullable=False, index=True)
    post_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    signal_type: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # e.g. 'founder_announcement', 'recruiter_post', 'funding_announcement'
    mentioned_role: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mentioned_stipend: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mentioned_remote: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mentioned_skills: Mapped[list[str] | None] = mapped_column(
        "mentioned_skills_jsonb", JSONB(astext_type=sa.Text()), nullable=True
    )
    contact_instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[float] = mapped_column(default=0.5, nullable=False)
    verification_status: Mapped[str] = mapped_column(
        String(50), default="social_lead_not_verified", nullable=False, index=True
    )
    verification_evidence: Mapped[dict | None] = mapped_column(
        "verification_evidence_jsonb", JSONB(astext_type=sa.Text()), nullable=True
    )
    is_indirect_signal: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index(
            "ix_social_signals_platform_post_url",
            "platform",
            "post_url",
            unique=True,
        ),
    )

    def __repr__(self) -> str:
        return f"<SocialSignal(id={self.id!r}, platform={self.platform!r}, post_url={self.post_url!r})>"