"""Geographic filtering and discovery keyword matching.

Implements the Phase 2 discovery logic:
- Title/keyword matching against 18 internship roles
- Description inspection for relevant technical work
- Geographic filtering for India-eligible remote positions
"""

import re

# ---------------------------------------------------------------------------
# Discovery keywords (titles). Matched case-insensitively against the job title.
# ---------------------------------------------------------------------------
INTERNSHIP_TITLE_KEYWORDS = [
    "software engineer intern",
    "software development intern",
    "full stack intern",
    "backend engineer intern",
    "frontend engineer intern",
    "ai engineer intern",
    "machine learning intern",
    "agent engineer intern",
    "llm engineer intern",
    "cybersecurity intern",
    "security engineer intern",
    "devops intern",
    "cloud engineer intern",
    "data engineer intern",
    "infrastructure engineer intern",
    "sre intern",
    "site reliability intern",
    "ml engineer intern",
    "artificial intelligence intern",
]

# Technical terms inspected in job descriptions when the title is not an
# explicit internship title but the work is relevant.
DESCRIPTION_RELEVANCE_TERMS = [
    "intern",
    "internship",
    "software engineer",
    "backend",
    "frontend",
    "full.stack",
    "machine learning",
    "ml engineer",
    "ai engineer",
    "artificial intelligence",
    "devops",
    "cloud engineer",
    "data engineer",
    "sre",
    "site reliability",
    "cybersecurity",
    "security engineer",
]

# Markers that a role is NOT India-eligible remote.
NON_INDIA_REMOTE_MARKERS = [
    "us only",
    "us-based",
    "united states only",
    "usa only",
    "eu only",
    "europe only",
    "uk only",
    "united kingdom only",
    "canada only",
    "singapore only",
    "australia only",
]

# Markers that suggest remote / worldwide / India eligibility.
REMOTE_POSITIVE_MARKERS = [
    "remote",
    "worldwide",
    "anywhere",
    "india",
    "indian",
    "bengaluru",
    "bangalore",
    "mumbai",
    "delhi",
    "hyderabad",
    "pune",
    "chennai",
    "kolkata",
]


def title_is_internship(title: str) -> bool:
    """Return True if the title matches an internship keyword."""
    title_l = title.lower()
    return any(k in title_l for k in INTERNSHIP_TITLE_KEYWORDS)


def description_is_relevant(description: str | None) -> bool:
    """Return True if the description mentions relevant internship/technical work."""
    if not description:
        return False
    text = description.lower()
    return any(t in text for t in DESCRIPTION_RELEVANCE_TERMS)


def is_india_eligible_remote(location: str | None, description: str | None) -> bool:
    """Geographic filtering for India-eligible remote positions.

    Include:
      - Fully remote open to Indian applicants
      - Remote explicitly allowing India
      - Worldwide remote
      - India-based remote

    Exclude:
      - US-only / EU-only / UK-only remote
      - Hybrid unless remote eligibility explicitly confirmed
      - Onsite positions

    We do NOT assume worldwide remote means India eligible — we require a
    positive signal (India/remote/worldwide) AND no explicit exclusion.
    """
    text = " ".join(filter(None, [location or "", description or ""])).lower()

    # Explicit exclusions take priority.
    for marker in NON_INDIA_REMOTE_MARKERS:
        if marker in text:
            return False

    # Onsite-only signals exclude.
    if "onsite" in text or "on-site" in text:
        if "remote" not in text:
            return False

    # Hybrid: only include if remote eligibility is explicitly confirmed.
    if "hybrid" in text:
        if not any(m in text for m in ["remote", "india", "worldwide"]):
            return False

    # Positive signal required.
    if not any(m in text for m in REMOTE_POSITIVE_MARKERS):
        return False

    return True


def opportunity_passes_filters(raw: dict[str, Any]) -> bool:
    """Apply discovery filters: title/description relevance + geography.

    Accepts a dict (e.g., a RawOpportunity as dict) with keys:
    - title: str
    - description_raw: str | None
    - location: str | None
    - description: str | None  (alternative key for description)
    """
    title = raw.get("title") or ""
    description = raw.get("description_raw") or raw.get("description") or ""

    # Title must be an internship OR description must show relevant work.
    if not title_is_internship(title) and not description_is_relevant(description):
        return False

    # Geographic filter.
    if not is_india_eligible_remote(raw.get("location"), description):
        return False

    return True