"""Lever public Postings API adapter.

Endpoint (public, no auth required):
    GET https://api.lever.co/v0/postings/{company}?mode=json

Docs: https://api.lever.co/v0/postings
"""

from typing import Any

from app.adapters.base import BaseAdapter, RawOpportunity
from app.crawling.http_client import CrawlError, HttpClient


class LeverAdapter(BaseAdapter):
    source = "lever"
    adapter_name = "lever"

    def __init__(self, company: str):
        self.company = company
        self._url = f"https://api.lever.co/v0/postings/{company}?mode=json"

    async def discover(self) -> list[RawOpportunity]:
        opportunities: list[RawOpportunity] = []
        async with HttpClient() as client:
            try:
                resp = await client.get(self._url)
            except CrawlError as exc:
                raise CrawlError(f"Lever company {self.company}: {exc}")

            if resp.status_code != 200:
                raise CrawlError(f"Lever company {self.company}: HTTP {resp.status_code}")

            postings: list[dict[str, Any]] = resp.json() or []

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
            created_at = p.get("createdAt")

            return RawOpportunity(
                source=self.source,
                source_id=f"lever:{post_id}",
                source_url=source_url,
                employer_url=None,
                title=title,
                company=self.company,
                company_url=None,
                description_raw=description_raw,
                location=location,
                is_remote=self._looks_remote(location, description_raw),
                is_paid=True,
                raw_payload=p,
            )
        except Exception:
            return None

    @staticmethod
    def _looks_remote(location: str | None, description: str | None) -> bool:
        text = " ".join(filter(None, [location or "", description or ""])).lower()
        return any(m in text for m in ["india", "remote", "worldwide", "anywhere"])