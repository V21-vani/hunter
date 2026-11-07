"""SmartRecruiters public job listings adapter.

Endpoint (public, no auth required):
    GET https://api.smartrecruiters.com/v1/companies/{companyId}/postings?limit=100&offset=0

Docs: https://developers.smartrecruiters.com/
"""

from typing import Any

from app.adapters.base import BaseAdapter, RawOpportunity
from app.crawling.http_client import CrawlError, HttpClient


class SmartRecruitersAdapter(BaseAdapter):
    source = "smartrecruiters"
    adapter_name = "smartrecruiters"

    def __init__(self, company_id: str):
        self.company_id = company_id
        self._url = (
            f"https://api.smartrecruiters.com/v1/companies/{company_id}/postings"
            f"?limit=100&offset=0"
        )

    async def discover(self) -> list[RawOpportunity]:
        opportunities: list[RawOpportunity] = []
        offset = 0
        limit = 100

        async with HttpClient() as client:
            while True:
                url = f"{self._url.split('?')[0]}?limit={limit}&offset={offset}"
                try:
                    resp = await client.get(url)
                except CrawlError as exc:
                    raise CrawlError(f"SmartRecruiters {self.company_id}: {exc}")

                if resp.status_code != 200:
                    break

                data: dict[str, Any] = resp.json() or {}
                postings = data.get("content") or []
                if not postings:
                    break

                for posting in postings:
                    opp = self._parse_posting(posting)
                    if opp:
                        opportunities.append(opp)

                total = data.get("totalFound", 0)
                offset += limit
                if offset >= total:
                    break

        return opportunities

    def _parse_posting(self, p: dict[str, Any]) -> RawOpportunity | None:
        try:
            post_id = p.get("id") or ""
            title = p.get("name") or ""
            if not post_id or not title:
                return None

            source_url = ""
            ref = p.get("ref") or {}
            if isinstance(ref, dict):
                source_url = ref.get("absoluteUri") or ""

            location = None
            job_ad = p.get("jobAd") or {}
            if isinstance(job_ad, dict):
                locations = job_ad.get("locations") or []
                if locations:
                    loc0 = locations[0]
                    if isinstance(loc0, dict):
                        parts = [
                            loc0.get("city"),
                            loc0.get("country"),
                        ]
                        location = ", ".join(p for p in parts if p) or None

            description_raw = None
            if isinstance(job_ad, dict):
                description_raw = job_ad.get("sections", {}).get("description", {}).get("text")

            return RawOpportunity(
                source=self.source,
                source_id=f"smartrecruiters:{post_id}",
                source_url=source_url,
                employer_url=None,
                title=title,
                company=self.company_id,
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