"""Pydantic schemas for ScanLog."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ScanLogBase(BaseModel):
    source_scanned: str = Field(..., min_length=1, max_length=255)
    start_time: datetime
    end_time: Optional[datetime] = None
    jobs_discovered: int = Field(default=0, ge=0)
    jobs_new: int = Field(default=0, ge=0)
    jobs_updated: int = Field(default=0, ge=0)
    errors: Optional[str] = None
    rate_limited: bool = False
    status: str = Field(default="running", max_length=50)


class ScanLogCreate(ScanLogBase):
    pass


class ScanLogUpdate(BaseModel):
    end_time: Optional[datetime] = None
    jobs_discovered: Optional[int] = Field(None, ge=0)
    jobs_new: Optional[int] = Field(None, ge=0)
    jobs_updated: Optional[int] = Field(None, ge=0)
    errors: Optional[str] = None
    rate_limited: Optional[bool] = None
    status: Optional[str] = Field(None, max_length=50)


class ScanLogOut(ScanLogBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)