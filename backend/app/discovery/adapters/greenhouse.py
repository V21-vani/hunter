"""Greenhouse Job Board API adapter.

Endpoint (public, no auth required):
    GET https://api.greenhouse.io/v1/boards/{board_id}/jobs?content=true
"""

from typing import Any

from app.discovery.adapters.base import BaseAdapter, RawOpportunity
from app.discovery.utils.geographic_filter import is_india_eligible_remote

DEFAULT_BOARD_ID = "acme"


class GreenhouseAdapter(BaseAdapter):
    source = "greenhouse"
    adapter_name = "greenhouse"

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)
        self.board_id = self.config.get("board_id", DEFAULT_BOARD_ID)
        self.company_name = self.config.get("company_name", self.board_id)
        self._url = f"https://api.greenhouse.io/v1/boards/{self.board_id}/jobs?content=true"

    async def discover(self) -> list[RawOpportunity]:
        opportunities: list[RawOpportunity] = []
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                resp = await client.get(self._url, timeout=30.0)
                resp.raise_for_status()
                data = resp.json()
        except Exception as exc:
            self.logger.warning(
                "Greenhouse fetch failed, returning empty",
                error=str(exc),
                board_id=self.board_id,
            )
            return opportunities

        for job in data.get("jobs", []):
            opp = self._parse_job(job)
            if opp:
                opportunities.append(opp)
        return opportunities

    def _parse_job(self, job: dict[str, Any]) -> RawOpportunity | None:
        try:
            job_id = str(job.get("id", ""))
            title = job.get("title") or ""
            if not job_id or not title:
                return None

            source_url = job.get("absolute_url") or ""
            location = None
            loc = job.get("location") or {}
            if isinstance(loc, dict):
                location = loc.get("name")

            description_raw = job.get("description") or None
            updated_at = job.get("updated_at")

            return RawOpportunity(
                source=self.source,
                source_id=f"greenhouse:{job_id}",
                source_url=source_url,
                employer_url=source_url,
                title=title,
                company=self.company_name,
                company_url=None,
                description_raw=description_raw,
                location=location,
                is_remote=is_india_eligible_remote(location, description_raw),
                is_paid=True,
                raw_payload=job,
            )
        except Exception:
            return None