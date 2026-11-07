"""Pydantic schemas for Verification."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, HttpUrl, Field


class VerificationBase(BaseModel):
    internship_id: UUID
    employer_verification_status: str = Field(default="pending", max_length=50)
    official_careers_url: Optional[HttpUrl] = None
    ats_confirmation: bool = False
    stipend_confirmation: bool = False
    remote_eligibility_confirmation: bool = False
    verification_evidence: Optional[dict] = None


class VerificationCreate(VerificationBase):
    pass


class VerificationUpdate(BaseModel):
    employer_verification_status: Optional[str] = Field(None, max_length=50)
    official_careers_url: Optional[HttpUrl] = None
    ats_confirmation: Optional[bool] = None
    stipend_confirmation: Optional[bool] = None
    remote_eligibility_confirmation: Optional[bool] = None
    verification_evidence: Optional[dict] = None


class VerificationOut(VerificationBase):
    id: UUID
    last_checked: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)