"""Pydantic schemas for social hiring intelligence."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SocialSignalBase(BaseModel):
    platform: str
    post_id: str
    post_text: str | None = None
    post_url: str
    post_date: datetime | None = None
    author: str | None = None
    author_role: str | None = None
    signal_type: str = "unknown"
    company: str | None = None
    mentioned_role: str | None = None
    mentioned_stipend: str | None = None
    mentioned_remote: str | None = None
    mentioned_skills: list[str] = []
    contact_instructions: str | None = None
    confidence_score: float = 0.5
    verification_status: str = "social_lead_not_verified"
    verification_evidence: dict[str, Any] | None = None
    is_indirect_signal: bool = False


class SocialSignalCreate(SocialSignalBase):
    pass


class SocialSignalUpdate(BaseModel):
    platform: str | None = None
    post_id: str | None = None
    post_text: str | None = None
    post_url: str | None = None
    post_date: datetime | None = None
    author: str | None = None
    author_role: str | None = None
    signal_type: str | None = None
    company: str | None = None
    mentioned_role: str | None = None
    mentioned_stipend: str | None = None
    mentioned_remote: str | None = None
    mentioned_skills: list[str] | None = None
    contact_instructions: str | None = None
    confidence_score: float | None = None
    verification_status: str | None = None
    verification_evidence: dict[str, Any] | None = None
    is_indirect_signal: bool | None = None


class SocialSignalOut(SocialSignalBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
