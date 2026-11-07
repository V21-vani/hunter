"""Workday public career pages adapter.

Workday exposes a tenant-specific JSON search endpoint:
    POST https://{tenant}.wd5.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs
    Body: {"appliedFacets": {}, "limit": 20, "offset": 0, "searchText": ""}
"""

from typing import Any

from app.discovery.adapters.base import BaseAdapter, RawOpportunity
from app.discovery.utils.geographic_filter import is_india_eligible_remote

DEFAULT_TENANT = "acme"
DEFAULT_SITE = "careers"


class WorkdayAdapter(BaseAdapter):
    source = "workday"
    adapter_name = "workday"

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)
        self.tenant = self.config.get("tenant", DEFAULT_TENANT)
        self.site = self.config.get("site", DEFAULT_SITE)
        self.company_name = self.config.get("company_name", self.tenant)
        self.search_text = self.config.get("search_text", "")
        self._url = (
            f"https://{self.tenant}.wd5.myworkdayjobs.com"
            f"/wday/cxs/{self.tenant}/{self.site}/jobs"
        )

    async def discover(self) -> list[RawOpportunity]:
        opportunities: list[RawOpportunity] = []
        try:
            import httpx

            offset = 0
            limit = 20
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }

            async with httpx.AsyncClient() as client:
                while True:
                    body = {
                        "appliedFacets": {},
                        "limit": limit,
                        "offset": offset,
                        "searchText": self.search_text,
                    }
                    resp = await client.post(self._url, json=body, headers=headers, timeout=30.0)
                    resp.raise_for_status()
                    data = resp.json() or {}

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
        except Exception as exc:
            self.logger.warning(
                "Workday fetch failed, returning empty",
                error=str(exc),
                tenant=self.tenant,
                site=self.site,
            )
            return opportunities

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

            return RawOpportunity(
                source=self.source,
                source_id=f"workday:{post_id}",
                source_url=source_url,
                employer_url=source_url,
                title=title,
                company=self.company_name,
                company_url=None,
                description_raw=None,
                location=location,
                is_remote=is_india_eligible_remote(location, None),
                is_paid=True,
            )
        except Exception:
            return None