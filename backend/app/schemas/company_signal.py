"""Pydantic schemas for CompanySignal."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, HttpUrl, Field


class CompanySignalBase(BaseModel):
    company_id: UUID
    signal_type: str = Field(..., min_length=1, max_length=50)
    source_url: Optional[HttpUrl] = None
    author: Optional[str] = Field(None, max_length=255)
    publication_date: Optional[datetime] = None
    signal_content: Optional[str] = None
    has_opening: bool = False


class CompanySignalCreate(CompanySignalBase):
    pass


class CompanySignalUpdate(BaseModel):
    signal_type: Optional[str] = Field(None, min_length=1, max_length=50)
    source_url: Optional[HttpUrl] = None
    author: Optional[str] = Field(None, max_length=255)
    publication_date: Optional[datetime] = None
    signal_content: Optional[str] = None
    has_opening: Optional[bool] = None


class CompanySignalOut(CompanySignalBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)