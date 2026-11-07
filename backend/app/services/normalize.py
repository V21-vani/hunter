"""Normalization: convert RawOpportunity -> canonical OpportunityCreate schema."""

from app.adapters.base import RawOpportunity
from app.schemas.opportunity import OpportunityCreate


def normalize(raw: RawOpportunity) -> OpportunityCreate:
    """Map a RawOpportunity to the canonical schema without filtering."""
    return OpportunityCreate(
        source=raw.source,
        source_id=raw.source_id,
        source_url=raw.source_url,
        employer_url=raw.employer_url,
        title=raw.title,
        company=raw.company,
        company_url=raw.company_url,
        description_raw=raw.description_raw,
        location=raw.location,
        is_remote=raw.is_remote,
        is_paid=raw.is_paid,
        stipend_min=raw.stipend_min,
        stipend_max=raw.stipend_max,
        stipend_currency=raw.stipend_currency,
        duration_min_months=raw.duration_min_months,
        duration_max_months=raw.duration_max_months,
        eligibility=raw.eligibility,
        application_url=raw.application_url,
        application_email=raw.application_email,
    )