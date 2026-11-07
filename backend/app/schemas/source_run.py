"""Pydantic schemas for source runs."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


from app.schemas.opportunity import OpportunityOut


class SourceRunBase(BaseModel):
    source: str
    adapter_name: str
    status: str = "running"
    opportunities_found: int = 0
    opportunities_new: int = 0
    opportunities_updated: int = 0
    error_message: str | None = None


class SourceRunOut(SourceRunBase):
    id: UUID
    started_at: datetime
    finished_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DiscoveryResult(BaseModel):
    source: str
    adapter_name: str
    found: int
    new: int
    updated: int
    opportunities: list[OpportunityOut]

    model_config = ConfigDict(from_attributes=True)


# Avoid circular import issue by referencing OpportunityOut lazily
DiscoveryResult.model_rebuild()