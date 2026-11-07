"""Deduplication helpers.

Dedupe by (source, source_id) exact match and fuzzy title+company matching
as a secondary safety net.
"""

from difflib import SequenceMatcher


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def is_duplicate_exact(
    existing: list[dict], source: str, source_id: str
) -> bool:
    return any(
        e.get("source") == source and e.get("source_id") == source_id
        for e in existing
    )


def is_duplicate_fuzzy(
    existing: list[dict], title: str, company: str, threshold: float = 0.92
) -> bool:
    for e in existing:
        et = e.get("title", "")
        ec = e.get("company", "")
        if _similarity(title, et) >= threshold and _similarity(company, ec) >= threshold:
            return True
    return False