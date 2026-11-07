"""Workday public career pages adapter.

Workday exposes a tenant-specific JSON search endpoint:
    POST https://{tenant}.wd5.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs
    Body: {"appliedFacets": {}, "limit": 20, "offset": 0, "searchText": ""}

This requires knowing the tenant and site name for each employer.
For companies without a known Workday endpoint, the CompanyCareerPageAdapter
falls back to HTML parsing of the career page.
"""

from typing import Any

from app.adapters.base import BaseAdapter, RawOpportunity
from app.crawling.http_client import CrawlError, HttpClient


class WorkdayAdapter(BaseAdapter):
    source = "workday"
    adapter_name = "workday"

    def __init__(
        self,
        tenant: str,
        site: str,
        company_name: str | None = None,
        search_text: str = "",
    ):
        self.tenant = tenant
        self.site = site
        self.company_name = company_name or tenant
        self.search_text = search_text
        self._url = (
            f"https://{tenant}.wd5.myworkdayjobs.com"
            f"/wday/cxs/{tenant}/{site}/jobs"
        )

    async def discover(self) -> list[RawOpportunity]:
        opportunities: list[RawOpportunity] = []
        offset = 0
        limit = 20
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        async with HttpClient() as client:
            while True:
                body: dict[str, Any] = {
                    "appliedFacets": {},
                    "limit": limit,
                    "offset": offset,
                    "searchText": self.search_text,
                }
                try:
                    resp = await client.post(self._url, json=body, headers=headers)
                except CrawlError as exc:
                    raise CrawlError(f"Workday {self.tenant}/{self.site}: {exc}")

                if resp.status_code != 200:
                    break

                data: dict[str, Any] = resp.json() or {}
                postings = data.get("jobPostings") or []
                if not postings:
                    break

                for posting in postings:
                    opp = self._parse_posting(posting)
                    if opp:
                        opportunities.append(opp)

                total = data.get("total", 0)
                offset += limit
                if offset >= total:
                    break

        return opportunities

    def _parse_posting(self, p: dict[str, Any]) -> RawOpportunity | None:
        try:
            post_id = p.get("id") or p.get("jobPostingId") or ""
            title = p.get("title") or ""
            if not post_id or not title:
                return None

            external_path = p.get("externalPath") or ""
            source_url = (
                f"https://{self.tenant}.wd5.myworkdayjobs.com{external_path}"
                if external_path
                else ""
            )

            location = None
            locations = p.get("locations") or []
            if locations:
                loc0 = locations[0]
                if isinstance(loc0, dict):
                    location = loc0.get("city") or loc0.get("country") or str(loc0)

            posted_on = p.get("postedOn") or p.get("startDate")

            return RawOpportunity(
                source=self.source,
                source_id=f"workday:{post_id}",
                source_url=source_url,
                employer_url=None,
                title=title,
                company=self.company_name,
                company_url=None,
                description_raw=None,
                location=location,
                is_remote=self._looks_remote(location, None),
                is_paid=True,
                raw_payload=p,
            )
        except Exception:
            return None

    @staticmethod
    def _looks_remote(location: str | None, description: str | None) -> bool:
        text = " ".join(filter(None, [location or "", description or ""])).lower()
        return any(m in text for m in ["india", "remote", "worldwide", "anywhere"])