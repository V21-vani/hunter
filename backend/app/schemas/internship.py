"""Pydantic schemas for Internship."""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, HttpUrl, Field


class InternshipBase(BaseModel):
    role_title: str = Field(..., min_length=1, max_length=255)
    company_id: Optional[UUID] = None
    role_category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    skills: Optional[list[str]] = None
    stipend_min: Optional[float] = Field(None, ge=0)
    stipend_max: Optional[float] = Field(None, ge=0)
    incentives: Optional[str] = None
    currency: str = Field(default="INR", max_length=10)
    remote_status: str = Field(default="onsite", max_length=50)
    india_eligible: bool = False
    duration_months: Optional[int] = Field(None, ge=1, le=24)
    weekly_hours: Optional[int] = Field(None, ge=1, le=168)
    experience_requirements: Optional[str] = Field(None, max_length=255)
    education_requirements: Optional[str] = Field(None, max_length=255)
    application_url: Optional[HttpUrl] = None
    original_posting_date: Optional[date] = None
    deadline: Optional[date] = None
    status: str = Field(default="discovered", max_length=50)


class InternshipCreate(InternshipBase):
    pass


class InternshipUpdate(BaseModel):
    role_title: Optional[str] = Field(None, min_length=1, max_length=255)
    company_id: Optional[UUID] = None
    role_category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    skills: Optional[list[str]] = None
    stipend_min: Optional[float] = Field(None, ge=0)
    stipend_max: Optional[float] = Field(None, ge=0)
    incentives: Optional[str] = None
    currency: Optional[str] = Field(None, max_length=10)
    remote_status: Optional[str] = Field(None, max_length=50)
    india_eligible: Optional[bool] = None
    duration_months: Optional[int] = Field(None, ge=1, le=24)
    weekly_hours: Optional[int] = Field(None, ge=1, le=168)
    experience_requirements: Optional[str] = Field(None, max_length=255)
    education_requirements: Optional[str] = Field(None, max_length=255)
    application_url: Optional[HttpUrl] = None
    original_posting_date: Optional[date] = None
    deadline: Optional[date] = None
    status: Optional[str] = Field(None, max_length=50)


class InternshipOut(InternshipBase):
    id: UUID
    first_discovered_date: datetime
    last_verified_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)