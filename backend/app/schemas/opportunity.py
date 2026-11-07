"""Pydantic schemas for opportunities."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OpportunityBase(BaseModel):
    source: str
    source_id: str
    source_url: str
    employer_url: str | None = None
    title: str
    company: str
    company_url: str | None = None
    description_raw: str | None = None
    location: str | None = None
    is_remote: bool = False
    is_paid: bool = False
    stipend_min: float | None = None
    stipend_max: float | None = None
    stipend_currency: str = "INR"
    duration_min_months: int | None = None
    duration_max_months: int | None = None
    eligibility: str | None = None
    application_url: str | None = None
    application_email: str | None = None


class OpportunityCreate(OpportunityBase):
    pass


class OpportunityUpdate(BaseModel):
    title: str | None = None
    company: str | None = None
    location: str | None = None
    is_remote: bool | None = None
    is_paid: bool | None = None
    stipend_min: float | None = None
    stipend_max: float | None = None
    description_raw: str | None = None
    status: str | None = None
    verification_status: str | None = None
    verification_evidence: dict[str, Any] | None = None


class OpportunityOut(OpportunityBase):
    id: UUID
    status: str
    verification_status: str
    rank_score: float | None = None
    discovered_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OpportunityList(BaseModel):
    items: list[OpportunityOut]
    total: int
    page: int
    page_size: int