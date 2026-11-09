"""Signal classification — classify raw post text into signal types."""

from __future__ import annotations

import re

# Import the phrase lists from signal_detection
from app.social.utils.signal_detection import (
    INDIRECT_SIGNAL_PHRASES,
    PRIMARY_HIRING_PHRASES,
    TECH_ROLE_KEYWORDS,
)
from app.social.utils.signal_detection import normalize


def classify_signal(post_text: str) -> str:
    """Classify a raw post into a signal type.

    Returns one of:
        - internship_post
        - engineering_follower_post
        - team_hiring_post
        - hiring_post
        - indirect_signal
        - unknown
    """
    normalized = normalize(post_text)
    for phrase in PRIMARY_HIRING_PHRASES:
        if phrase in normalized:
            if "intern" in normalized or "student" in normalized:
                return "internship_post"
            if "engineering" in normalized or "engineer" in normalized:
                return "engineering_follower_post"
            if "hiring" in normalized and "team" in normalized:
                return "team_hiring_post"
            return "hiring_post"
    for phrase in INDIRECT_SIGNAL_PHRASES:
        if phrase in normalized:
            return "indirect_signal"
    return "unknown"


def is_indirect_signal(post_text: str) -> bool:
    """Check if the post contains only indirect signal phrases."""
    normalized = normalize(post_text)
    for phrase in INDIRECT_SIGNAL_PHRASES:
        if phrase in normalized:
            return True
    return False


def classify_company_signal(post_text: str) -> dict[str, Any] | None:
    """Classify a post as a company signal (funding, expansion, etc.).

    Returns a dict with signal_type and processed data, or None if not a
    company signal.
    """
    normalized = normalize(post_text)
    for phrase in INDIRECT_SIGNAL_PHRASES:
        if phrase in normalized:
            return {
                "signal_type": "indirect_signal",
                "is_indirect": True,
            }
    return None