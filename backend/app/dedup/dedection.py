"""Deduplication module for internship opportunities."""

from typing import Optional
import re

from app.db.models.internship import Internship


def normalize_text(text: str) -> str:
    """Normalize text for comparison: lowercase, strip punctuation, collapse whitespace."""
    if not text:
        return ""
    t = text.lower().strip()
    t = re.sub(r"[^\w\s]", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t


def company_normalized(name: str) -> str:
    """Normalize company name for deduplication."""
    return normalize_text(name)


def title_normalized(title: str) -> str:
    """Normalize job title for deduplication."""
    return normalize_text(title)


def _title_similarity(a: str, b: str) -> float:
    """Compute Jaccard similarity on normalized title words."""
    set_a = set(a.split())
    set_b = set(b.split())
    if not set_a and not set_b:
        return 1.0
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union


def _location_stipend_match(existing: dict, new: dict) -> bool:
    """Check if location and stipend are compatible for deduplication."""
    loc_match = (existing["location"] or "") == (new["location"] or "") or (
        existing["location"] and new["location"] and
        existing["location"].lower() == new["location"].lower()
    )
    stipend_match = (
        existing["stipend"] is None and new["stipend"] is None
    ) or (
        existing["stipend"] is not None and new["stipend"] is not None
        and abs(existing["stipend"] - new["stipend"]) < 2000
    )
    return loc_match and stipend_match


def deduplicate_internships(
    existing: list[Internship],
    new_internship: Internship,
    similarity_threshold: float = 0.92,
) -> tuple[bool, Internship]:
    """Check if new_internship is a duplicate of existing internships.

    Returns (is_duplicate, merged_internship).
    """
    new_norm = {
        "company": company_normalized(new_internship.company),
        "title": title_normalized(new_internship.role_title),
        "application_url": new_internship.application_url,
        "ats_id": new_internship.source_id,
        "location": new_internship.location,
        "stipend": new_internship.stipend_min,
    }

    for existing in existing:
        existing_norm = {
            "company": company_normalized(existing.company),
            "title": title_normalized(existing.role_title),
            "application_url": existing.application_url,
            "ats_id": existing.source_id,
            "location": existing.location,
            "stipend": existing.stipend_min,
        }

        # Criterion 1: Same company + same application URL/ATS ID
        if (existing_norm["company"] == new_norm["company"] and
                (existing_norm["application_url"] == new_norm["application_url"] or
                 existing_norm["ats_id"] == new_norm["ats_id"])):
            return True, existing

        # Criterion 2: High title similarity + same company + same location/stipend
        title_sim = _title_similarity(existing_norm["title"], new_norm["title"])
        if (title_sim >= 0.92 and
                existing_norm["company"] == new_norm["company"] and
                _location_stipend_match(existing_norm, new_norm)):
            return True, existing

    return False, new_internship