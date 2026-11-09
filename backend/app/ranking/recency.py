"""Recency ranking module for internship postings.

Recency priority ordering:
1. 0–7 days (fresh — highest priority)
2. 8–14 days (recent)
3. 15–30 days, only if employer page confirms opening is still active
4. >30 days (excluded by default)

Critical: Do not confuse:
- Original publication date
- ATS last updated date
- Search engine crawl date
- First discovery date
- Last verification date
"""

from datetime import datetime, timedelta
from typing import Optional


def days_since_publication(publication_date: Optional[datetime]) -> Optional[int]:
    """Return days since original publication date, or None if date missing."""
    if not publication_date:
        return None
    delta = datetime.utcnow() - publication_date
    return delta.days


def is_recent(publication_date: Optional[datetime], current_date: Optional[datetime] = None) -> bool:
    """Return True if the posting is within the recency window.

    Window:
    - 0–7 days: always fresh
    - 8–14 days: recent
    - 15–30 days: only if employer page confirms active opening
    - >30 days: excluded by default
    """
    days = days_since_publication(publication_date)
    if days is None:
        return False

    if days <= 7:
        return True  # always fresh
    if days <= 14:
        return True  # recent
    if days <= 30:
        # only fresh if employer confirms active — caller must provide confirmation
        return False  # default: exclude unless confirmed
    return False  # >30 days: excluded


def is_recruitment_stale(publication_date: Optional[datetime],
                       employer_confirms_active: bool = False) -> bool:
    """Return True if the posting should be considered stale.

    Stale = >30 days old, OR >15 days old without employer confirmation.
    """
    days = days_since_publication(publication_date)
    if days is None:
        return True  # no date = treat as stale
    if days > 30:
        return True  # always stale after 30 days
    if days > 15 and not employer_confirms_active:
        return True  # stale after 15 days without confirmation
    return False