"""Social Hiring Intelligence Engine — orchestrates all social platform adapters.

The SocialEngine:
1. Instantiates all registered social platform adapters.
2. Runs each adapter to fetch raw post data.
3. Runs signal detection and entity extraction on raw posts.
4. Classifies signals (primary / indirect).
5. Marks all as SOCIAL LEAD — NOT VERIFIED (per Phase 3 requirement).
6. Persists via the Phase 1 database layer.
7. Returns a structured report.

This engine is independent of the ATS discovery engine and can be run
on a scheduled basis (e.g., hourly, daily).
"""

from __future__ import annotations

import time
from typing import Any

from app.core.logging import get_logger
from app.social.models.social_signal import SocialSignal
from app.db.repositories.social_signal_repository import SocialSignalRepository
from app.social.adapters.registry import instantiate, list_platforms
from app.social.services.social_signal_service import SocialSignalService

logger = get_logger(__name__)


class SocialEngine:
    """Orchestrates social hiring intelligence discovery across all platforms."""

    def __init__(
        self,
        adapter_configs: dict[str, dict[str, Any]] | None = None,
        session=None,
    ):
        """
        Args:
            adapter_configs: Mapping of platform name to adapter config kwargs.
                Example:
                    {
                        "linkedin": {"companies": ["acme", "startup"]},
                        "reddit": {"subreddits": ["hiring", "startups"]},
                    }
            session: SQLAlchemy session (optional — for persistence).
        """
        self.adapter_configs = adapter_configs or {}
        self.session = session
        self._adapters: dict[str, Any] = {}

    def _get_adapter(self, platform: str) -> Any:
        """Get or create an adapter instance for the given platform."""
        if platform not in self._adapters:
            adapter_cls = instantiate(platform, self.adapter_configs.get(platform))
            if adapter_cls is None:
                logger.warning("No adapter registered for platform", platform=platform)
                self._adapters[platform] = None
            else:
                self._adapters[platform] = adapter_cls
        return self._adapters[platform]

    async def discover_single(self, platform: str) -> dict[str, Any]:
        """Run discovery for a single platform adapter."""
        adapter = self._get_adapter(platform)
        if adapter is None:
            return {"platform": platform, "found": 0, "processed": 0, "error": "No adapter"}

        start = time.time()
        try:
            raw_posts = await adapter.run()
            service = SocialSignalService(self.session)
            signals = service.process_batch(raw_posts)

            logger.info(
                "Social adapter complete",
                platform=platform,
                found=len(raw_posts),
                processed=len(signals),
                elapsed_seconds=round(time.time() - start, 2),
            )

            return {
                "platform": platform,
                "adapter_name": adapter.adapter_name,
                "found": len(raw_posts),
                "processed": len(signals),
                "elapsed_seconds": round(time.time() - start, 2),
                "signals": [s.post_id for s in signals],
            }
        except Exception as exc:
            logger.exception("Platform adapter failed", platform=platform, error=str(exc))
            return {
                "platform": platform,
                "found": 0,
                "processed": 0,
                "error": str(exc),
            }

    async def discover_all(self) -> dict[str, Any]:
        """Run discovery for all registered social platforms."""
        report = {
            "total_found": 0,
            "total_processed": 0,
            "platforms_run": [],
            "errors": [],
            "signals": [],
        }

        for platform in list_platforms():
            result = await self.discover_single(platform)
            report["platforms_run"].append(result)
            report["total_found"] += result.get("found", 0)
            report["total_processed"] += result.get("processed", 0)
            if result.get("error"):
                report["errors"].append({"platform": platform, "error": result["error"]})

        # Collect signal IDs
        for src in report["platforms_run"]:
            if src.get("signals"):
                report["signals"].extend(src["signals"])

        return report

    def get_signals_by_company(self, company: str, limit: int = 50) -> list[SocialSignal]:
        """Retrieve all signals for a company."""
        service = SocialSignalService(self.session)
        return service.get_by_company(company=company, limit=limit)
