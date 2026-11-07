"""Ashby public job posting board adapter."""

from typing import Any

from app.discovery.adapters.base import BaseAdapter, RawOpportunity
from app.discovery.utils.geographic_filter import is_india_eligible_remote

DEFAULT_COMPANY = "acme"


class AshbyAdapter(BaseAdapter):
    source = "ashby"
    adapter_name = "ashby"

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)
        self.company = self.config.get("company", DEFAULT_COMPANY)
        self._url = "https://api.ashbyhq.com/job-posting-board"

    async def discover(self) -> list[RawOpportunity]:
        opportunities: list[RawOpportunity] = []
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    self._url, json={"identifier": self.company}, timeout=30.0
                )
                resp.raise_for_status()
                data = resp.json() or {}
        except Exception as exc:
            self.logger.warning(
                "Ashby fetch failed, returning empty",
                error=str(exc),
                company=self.company,
            )
            return opportunities

        board = data.get("jobPostingBoard") or {}
        postings = board.get("jobPostings") or []

        for posting in postings:
            opp = self._parse_posting(posting)
            if opp:
                opportunities.append(opp)
        return opportunities

    def _parse_posting(self, p: dict[str, Any]) -> RawOpportunity | None:
        try:
            post_id = p.get("id") or ""
            title = p.get("title") or ""
            if not post_id or not title:
                return None

            source_url = p.get("jobUrl") or ""
            location_parts = []
            loc = p.get("location") or {}
            if isinstance(loc, dict):
                for k in ("city", "state", "country"):
                    if loc.get(k):
                        location_parts.append(str(loc[k]))
            location = ", ".join(location_parts) or None

            description_raw = p.get("descriptionHtml") or p.get("description") or None

            return RawOpportunity(
                source=self.source,
                source_id=f"ashby:{post_id}",
                source_url=source_url,
                employer_url=source_url,
                title=title,
                company=self.company,
                company_url=None,
                description_raw=description_raw,
                location=location,
                is_remote=is_india_eligible_remote(location, description_raw),
                is_paid=True,
            )
        except Exception:
            return None