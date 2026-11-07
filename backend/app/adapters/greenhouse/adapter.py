"""Greenhouse public Job Board API adapter.

Endpoint (public, no auth required):
    GET https://api.greenhouse.io/v1/boards/{board_id}/jobs?content=true

Docs: https://developers.greenhouse.io/harvesting#job-postings
"""

from typing import Any

from app.adapters.base import BaseAdapter, RawOpportunity
from app.crawling.http_client import CrawlError, HttpClient


class GreenhouseAdapter(BaseAdapter):
    source = "greenhouse"
    adapter_name = "greenhouse"

    def __init__(self, board_id: str, company_name: str | None = None):
        self.board_id = board_id
        self.company_name = company_name or board_id
        self._url = f"https://api.greenhouse.io/v1/boards/{board_id}/jobs?content=true"

    async def discover(self) -> list[RawOpportunity]:
        opportunities: list[RawOpportunity] = []
        async with HttpClient() as client:
            try:
                resp = await client.get(self._url)
            except CrawlError as exc:
                raise CrawlError(f"Greenhouse board {self.board_id}: {exc}")

            if resp.status_code != 200:
                raise CrawlError(
                    f"Greenhouse board {self.board_id}: HTTP {resp.status_code}"
                )

            data: dict[str, Any] = resp.json()
            jobs = data.get("jobs", [])

        for job in jobs:
            opp = self._parse_job(job)
            if opp:
                opportunities.append(opp)
        return opportunities

    def _parse_job(self, job: dict[str, Any]) -> RawOpportunity | None:
        try:
            job_id = str(job.get("id", ""))
            title = job.get("title") or ""
            if not title or not job_id:
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
                employer_url=None,
                title=title,
                company=self.company_name,
                company_url=None,
                description_raw=description_raw,
                location=location,
                is_remote=self._looks_remote(location, description_raw),
                is_paid=True,  # Greenhouse postings are typically paid roles; set True, refined later
                raw_payload=job,
                discovered_at=self._parse_ts(updated_at),
            )
        except Exception:
            return None

    @staticmethod
    def _looks_remote(location: str | None, description: str | None) -> bool:
        text = " ".join(filter(None, [location or "", description or ""])).lower()
        india_markers = ["india", "remote", "worldwide", "anywhere"]
        return any(m in text for m in india_markers)

    @staticmethod
    def _parse_ts(value: str | None):
        from datetime import datetime, timezone

        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None