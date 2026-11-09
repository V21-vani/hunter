"""Base adapter for social hiring platforms."""

from abc import ABC, abstractmethod
from typing import Any

from app.social.models.social_signal import SocialSignal


class BaseSocialAdapter(ABC):
    """Abstract base class for social hiring platform adapters.

    Each adapter implements discover() which returns a list of raw post
    data (dicts) that the service layer converts to SocialSignal objects.

    IMPORTANT: Per the Phase 3 requirements, adapters must only access
    publicly available content. Private accounts, groups, and restricted
    content are never scraped. Bypassing logins, rate limits, CAPTCHAs,
    or platform restrictions is prohibited.
    """

    platform: str = ""
    adapter_name: str = ""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

    @property
    def logger(self):
        import structlog
        return structlog.get_logger(f"internradar.social.adapters.{self.__class__.__name__}")

    @property
    def source_name(self) -> str:
        return self.platform

    @abstractmethod
    async def discover(self) -> list[dict[str, Any]]:
        """Fetch raw post data from the platform and return as list of dicts.

        Each dict must contain:
            - post_id
            - post_text (or content)
            - post_url
            - post_date
            - author (optional)
            - author_role (optional)
        """
        raise NotImplementedError

    async def run(self) -> list[dict[str, Any]]:
        """Run discovery and return raw post data."""
        return await self.discover()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(platform={self.platform!r})>"
