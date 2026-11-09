"""Deduplication module for internship opportunities."""

from app.dedup.dedection import (
    deduplicate_internships,
    deduplicate_social_signals,
    deduplicate_internship_sources,
    normalize_text,
    company_normalized,
    title_normalized,
    _title_similarity,
    _location_stipend_match,
)