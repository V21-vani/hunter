"""Base adapter and RawOpportunity dataclass."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class RawOpportunity:
    """Unnormalized opportunity as returned by a source adapter.

    Every adapter must populate at least: source, source_id, source_url,
    title, company. All other fields are optional and filled during
    normalization/enrichment in the Phase 1 database layer.
    """

    source: str
    source_id: str
    source_url: str
    employer_url: str | None = None
    title: str = ""
    company: str = ""
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
    discovered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    raw_payload: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "source_id": self.source_id,
            "source_url": self.source_url,
            "employer_url": self.employer_url,
            "title": self.title,
            "company": self.company,
            "company_url": self.company_url,
            "description_raw": self.description_raw,
            "location": self.location,
            "is_remote": self.is_remote,
            "is_paid": self.is_paid,
            "stipend_min": self.stipend_min,
            "stipend_max": self.stipend_max,
            "stipend_currency": self.stipend_currency,
            "duration_min_months": self.duration_min_months,
            "duration_max_months": self.duration_max_months,
            "eligibility": self.eligibility,
            "application_url": self.application_url,
            "application_email": self.application_email,
            "discovered_at": self.discovered_at,
        }


class BaseAdapter:
    """Abstract base class for all source adapters.

    Each adapter must implement discover() which fetches raw opportunities.
    The discovery engine applies filtering (title keywords, description
    inspection, geographic filtering) on top of the adapter output.
    """

    source: str = ""
    adapter_name: str = ""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

    @property
    def logger(self):
        import structlog

        return structlog.get_logger(f"internradar.discovery.adapters.{self.__class__.__name__}")

    @property
    def source_name(self) -> str:
        return self.source

    async def discover(self) -> list[RawOpportunity]:
        """Fetch and return raw opportunities from this source."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement discover()")

    async def run(self) -> list[RawOpportunity]:
        """Run discovery with timing. Override only for custom behaviour."""
        return await self.discover()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(source={self.source!r})>"