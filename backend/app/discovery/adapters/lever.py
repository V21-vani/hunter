"""Lever public Postings API adapter."""

from typing import Any

from app.discovery.adapters.base import BaseAdapter, RawOpportunity
from app.discovery.utils.geographic_filter import is_india_eligible_remote

DEFAULT_COMPANY = "acme"


class LeverAdapter(BaseAdapter):
    source = "lever"
    adapter_name = "lever"

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)
        self.company = self.config.get("company", DEFAULT_COMPANY)
        self._url = f"https://api.lever.co/v0/postings/{self.company}?mode=json"

    async def discover(self) -> list[RawOpportunity]:
        opportunities: list[RawOpportunity] = []
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                resp = await client.get(self._url, timeout=30.0)
                resp.raise_for_status()
                postings = resp.json() or []
        except Exception as exc:
            self.logger.warning(
                "Lever fetch failed, returning empty",
                error=str(exc),
                company=self.company,
            )
            return opportunities

        for posting in postings:
            opp = self._parse_posting(posting)
            if opp:
                opportunities.append(opp)
        return opportunities

    def _parse_posting(self, p: dict[str, Any]) -> RawOpportunity | None:
        try:
            post_id = p.get("id") or ""
            title = p.get("text") or ""
            if not post_id or not title:
                return None

            source_url = p.get("applyUrl") or ""
            location = None
            categories = p.get("categories") or {}
            if isinstance(categories, dict):
                location = categories.get("location")

            description_raw = p.get("description") or None

            return RawOpportunity(
                source=self.source,
                source_id=f"lever:{post_id}",
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