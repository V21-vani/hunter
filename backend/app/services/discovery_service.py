"""Discovery service — orchestrates adapter discovery, filtering, normalization,
and persistence. Implements the discovery logic (title/keyword + description
inspection) and geographic filtering (India-eligible remote)."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.adapters.base import RawOpportunity
from app.adapters.registry import instantiate
from app.core.logging import get_logger
from app.db.models.opportunity import Opportunity
from app.db.models.source_run import SourceRun
from app.db.session import SessionLocal
from app.services.dedupe import is_duplicate_exact, is_duplicate_fuzzy
from app.services.normalize import normalize

logger = get_logger(__name__)

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
    """Geographic filtering.

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


def opportunity_passes_filters(raw: RawOpportunity) -> bool:
    """Apply discovery filters: title/description relevance + geography."""
    if not title_is_internship(raw.title) and not description_is_relevant(
        raw.description_raw
    ):
        return False
    if not is_india_eligible_remote(raw.location, raw.description_raw):
        return False
    return True


class DiscoveryService:
    """Orchestrates discovery across all registered adapters."""

    def __init__(self, db: Session | None = None):
        self.db = db or SessionLocal()

    def __enter__(self) -> "DiscoveryService":
        return self

    def __exit__(self, *args: Any) -> None:
        if self.db is not None:
            self.db.close()

    def discover_source(
        self, source: str, adapter_kwargs: dict[str, Any]
    ) -> list[RawOpportunity]:
        """Run a single adapter and return filtered raw opportunities."""
        adapter = instantiate(source, **adapter_kwargs)
        if adapter is None:
            logger.warning("No adapter registered for source", source=source)
            return []

        logger.info("Running adapter", source=source, adapter=adapter.adapter_name)

        run = SourceRun(
            source=source,
            adapter_name=adapter.adapter_name,
            status="running",
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)

        try:
            raw_opps = adapter.run()
            filtered = [o for o in raw_opps if opportunity_passes_filters(o)]
            logger.info(
                "Adapter complete",
                source=source,
                found=len(raw_opps),
                passed_filters=len(filtered),
            )
            run.opportunities_found = len(raw_opps)
            run.status = "completed"
            self.db.commit()
            return filtered
        except Exception as exc:  # noqa: BLE001
            logger.exception("Adapter failed", source=source, error=str(exc))
            run.status = "failed"
            run.error_message = str(exc)
            self.db.commit()
            return []

    def persist(
        self, raw_opportunities: list[RawOpportunity]
    ) -> tuple[int, int]:
        """Persist filtered opportunities, deduping by (source, source_id).

        Returns (new_count, updated_count).
        """
        new_count = 0
        updated_count = 0

        for raw in raw_opportunities:
            schema_in = normalize(raw)

            existing = (
                self.db.query(Opportunity)
                .filter_by(source=schema_in.source, source_id=schema_in.source_id)
                .first()
            )

            if existing:
                changed = False
                for field in [
                    "title", "company", "location", "description_raw",
                    "is_remote", "is_paid", "application_url",
                ]:
                    new_val = getattr(schema_in, field)
                    old_val = getattr(existing, field)
                    if new_val != old_val:
                        setattr(existing, field, new_val)
                        changed = True
                if changed:
                    updated_count += 1
                continue

            all_opps = (
                self.db.query(Opportunity)
                .filter_by(company=schema_in.company)
                .all()
            )
            existing_dicts = [
                {
                    "source": o.source,
                    "source_id": o.source_id,
                    "title": o.title,
                    "company": o.company,
                }
                for o in all_opps
            ]
            if is_duplicate_exact(existing_dicts, schema_in.source, schema_in.source_id):
                continue
            if is_duplicate_fuzzy(existing_dicts, schema_in.title, schema_in.company):
                continue

            opp = Opportunity(**schema_in.model_dump())
            self.db.add(opp)
            new_count += 1

        self.db.commit()
        return new_count, updated_count

    def run_source_and_persist(
        self, source: str, adapter_kwargs: dict[str, Any]
    ) -> dict[str, int]:
        """Convenience: discover a source and persist results."""
        raw_opps = self.discover_source(source, adapter_kwargs)
        new_count, updated_count = self.persist(raw_opps)
        return {
            "source": source,
            "found": len(raw_opps),
            "new": new_count,
            "updated": updated_count,
        }


def discover_and_persist(
    source: str, adapter_kwargs: dict[str, Any], db: Session | None = None
) -> dict[str, int]:
    with DiscoveryService(db) as svc:
        return svc.run_source_and_persist(source, adapter_kwargs)
