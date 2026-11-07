"""Abstract base class for all source adapters."""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class RawOpportunity:
    """Unnormalized opportunity as returned by a source adapter.

    Every adapter must populate at least: source, source_id, source_url,
    title, company. All other fields are optional and filled during
    normalization/enrichment.
    """

    source: str
    source_id: str
    source_url: str
    title: str
    company: str
    employer_url: str | None = None
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


class BaseAdapter(ABC):
    """Every adapter implements discover() and returns RawOpportunity objects."""

    source: str = ""
    adapter_name: str = ""

    @abstractmethod
    async def discover(self) -> list[RawOpportunity]:
        """Fetch and return raw opportunities from this source."""
        ...

    async def run(self) -> list[RawOpportunity]:
        """Run discovery with timing. Override only for custom behaviour."""
        return await self.discover()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(source={self.source!r})>"