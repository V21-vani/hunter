"""DiscoveryEngine — orchestrates the full discovery pipeline.

The engine:
1. Instantiates all registered source adapters.
2. Runs each adapter to fetch raw opportunities.
3. Applies discovery filters (title/description/geographic).
4. Normalizes filtered opportunities into the Phase 1 database schema.
5. Persists them via the Phase 1 service layer.
6. Returns a structured report of what was discovered.

This engine is independent of the Phase 1 database layer by default;
it can be wired to the Phase 1 service layer for persistence.
"""

from __future__ import annotations

import time
from typing import Any

from app.adapters.base import RawOpportunity
from app.adapters.registry import instantiate, list_sources
from app.core.logging import get_logger
from app.discovery.utils.geographic_filter import (
    description_is_relevant,
    is_india_eligible_remote,
    opportunity_passes_filters,
    title_is_internship,
)

logger = get_logger(__name__)


class DiscoveryEngine:
    """Orchestrates discovery across all registered source adapters."""

    def __init__(self, adapter_configs: dict[str, dict[str, Any]] | None = None):
        """
        Args:
            adapter_configs: Mapping of source name to adapter config kwargs.
                Example:
                    {
                        "greenhouse": {"board_id": "acme"},
                        "lever": {"company": "acme"},
                        "ashby": {"company": "acme"},
                        "smartrecruiters": {"company_id": "acme"},
                        "workday": {"tenant": "acme", "site": "careers"},
                    }
        """
        self.adapter_configs = adapter_configs or {}
        self._adapters: dict[str, Any] = {}

    def _get_adapter(self, source: str) -> Any:
        """Get or create an adapter instance for the given source."""
        if source not in self._adapters:
            adapter_cls = instantiate(source, self.adapter_configs.get(source))
            if adapter_cls is None:
                logger.warning("No adapter registered for source", source=source)
                self._adapters[source] = None
            else:
                self._adapters[source] = adapter_cls
        return self._adapters[source]

    async def discover_single(self, source: str) -> dict[str, Any]:
        """Run discovery for a single source adapter."""
        adapter = self._get_adapter(source)
        if adapter is None:
            return {"source": source, "found": 0, "passed_filters": 0}

        start = time.time()
        try:
            raw_opps = await adapter.run()
            filtered = [o for o in raw_opps if opportunity_passes_filters(o.to_dict())]
            elapsed = time.time() - start

            logger.info(
                "Adapter complete",
                source=source,
                found=len(raw_opps),
                passed_filters=len(filtered),
                elapsed_seconds=round(elapsed, 2),
            )

            return {
                "source": source,
                "adapter_name": adapter.adapter_name,
                "found": len(raw_opps),
                "passed_filters": len(filtered),
                "elapsed_seconds": round(elapsed, 2),
                "opportunities": [o.to_dict() for o in filtered],
            }
        except Exception as exc:
            logger.exception("Adapter failed", source=source, error=str(exc))
            return {
                "source": source,
                "found": 0,
                "passed_filters": 0,
                "error": str(exc),
            }

    async def discover_all(self) -> dict[str, Any]:
        """Run discovery for all registered adapters and return a report."""
        report = {
            "total_found": 0,
            "total_passed_filters": 0,
            "sources_run": [],
            "errors": [],
        }

        for source in list_sources():
            result = await self.discover_single(source)
            report["sources_run"].append(result)
            report["total_found"] += result.get("found", 0)
            report["total_passed_filters"] += result.get("passed_filters", 0)
            if result.get("error"):
                report["errors"].append({
                    "source": source,
                    "error": result["error"],
                })

        return report

    @staticmethod
    def normalize_raw(raw: dict[str, Any]) -> dict[str, Any]:
        """Normalize a RawOpportunity dict to the Phase 1 database schema.

        This is a passthrough that ensures all required Phase 1 fields
        are present with safe defaults. Actual type conversion and
        database persistence should go through a Phase 1 repository.
        """
        return {
            "source": raw.get("source", "unknown"),
            "source_id": raw.get("source_id", ""),
            "source_url": raw.get("source_url", ""),
            "employer_url": raw.get("employer_url"),
            "title": raw.get("title", ""),
            "company": raw.get("company", ""),
            "company_url": raw.get("company_url"),
            "description_raw": raw.get("description_raw"),
            "location": raw.get("location"),
            "is_remote": raw.get("is_remote", False),
            "is_paid": raw.get("is_paid", False),
            "stipend_min": raw.get("stipend_min"),
            "stipend_max": raw.get("stipend_max"),
            "stipend_currency": raw.get("stipend_currency", "INR"),
            "duration_min_months": raw.get("duration_min_months"),
            "duration_max_months": raw.get("duration_max_months"),
            "eligibility": raw.get("eligibility"),
            "application_url": raw.get("application_url"),
            "application_email": raw.get("application_email"),
            "discovered_at": raw.get("discovered_at"),
        }