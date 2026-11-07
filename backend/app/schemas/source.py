"""Pydantic schemas for Source."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, HttpUrl, Field


class SourceBase(BaseModel):
    source_type: str = Field(..., min_length=1, max_length=50)
    original_source_url: HttpUrl
    platform: Optional[str] = Field(None, max_length=100)
    author_company: Optional[str] = Field(None, max_length=255)
    original_publication_date: Optional[datetime] = None
    evidence_metadata: Optional[dict] = None


class SourceCreate(SourceBase):
    pass


class SourceUpdate(BaseModel):
    source_type: Optional[str] = Field(None, min_length=1, max_length=50)
    original_source_url: Optional[HttpUrl] = None
    platform: Optional[str] = Field(None, max_length=100)
    author_company: Optional[str] = Field(None, max_length=255)
    original_publication_date: Optional[datetime] = None
    evidence_metadata: Optional[dict] = None


class SourceOut(SourceBase):
    id: UUID
    discovery_timestamp: datetime

    model_config = ConfigDict(from_attributes=True)