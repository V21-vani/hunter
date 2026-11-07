"""Pydantic schemas for Company."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, HttpUrl, Field


class CompanyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    website: Optional[HttpUrl] = None
    linkedin_url: Optional[HttpUrl] = None
    industry: Optional[str] = Field(None, max_length=100)
    company_size: Optional[str] = Field(None, max_length=50)
    headquarters: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    careers_url: Optional[HttpUrl] = None
    verification_status: str = Field(default="unverified", max_length=50)
    is_actively_hiring: bool = False


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    website: Optional[HttpUrl] = None
    linkedin_url: Optional[HttpUrl] = None
    industry: Optional[str] = Field(None, max_length=100)
    company_size: Optional[str] = Field(None, max_length=50)
    headquarters: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    careers_url: Optional[HttpUrl] = None
    verification_status: Optional[str] = Field(None, max_length=50)
    is_actively_hiring: Optional[bool] = None


class CompanyOut(CompanyBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)