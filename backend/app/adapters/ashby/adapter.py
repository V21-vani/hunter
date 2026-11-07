"""Ashby public job posting board adapter.

Endpoint (public, no auth required):
    POST https://api.ashbyhq.com/job-posting-board
    Body: {"identifier": "{company}"}

Docs: https://ashbyhq.com/api
"""

from typing import Any

from app.adapters.base import BaseAdapter, RawOpportunity
from app.crawling.http_client import CrawlError, HttpClient


class AshbyAdapter(BaseAdapter):
    source = "ashby"
    adapter_name = "ashby"

    def __init__(self, company: str):
        self.company = company
        self._url = "https://api.ashbyhq.com/job-posting-board"

    async def discover(self) -> list[RawOpportunity]:
        opportunities: list[RawOpportunity] = []
        async with HttpClient() as client:
            try:
                resp = await client.post(self._url, json={"identifier": self.company})
            except CrawlError as exc:
                raise CrawlError(f"Ashby company {self.company}: {exc}")

            if resp.status_code != 200:
                raise CrawlError(f"Ashby company {self.company}: HTTP {resp.status_code}")

            data: dict[str, Any] = resp.json() or {}
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
            location_parts: list[str] = []
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