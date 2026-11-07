"""SmartRecruiters public job listings adapter."""

from typing import Any

from app.discovery.adapters.base import BaseAdapter, RawOpportunity
from app.discovery.utils.geographic_filter import is_india_eligible_remote

DEFAULT_COMPANY_ID = "acme"


class SmartRecruitersAdapter(BaseAdapter):
    source = "smartrecruiters"
    adapter_name = "smartrecruiters"

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)
        self.company_id = self.config.get("company_id", DEFAULT_COMPANY_ID)
        self._url = (
            f"https://api.smartrecruiters.com/v1/companies/{self.company_id}/postings"
        )

    async def discover(self) -> list[RawOpportunity]:
        opportunities: list[RawOpportunity] = []
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                offset = 0
                limit = 100
                while True:
                    url = f"{self._url}?limit={limit}&offset={offset}"
                    resp = await client.get(url, timeout=30.0)
                    resp.raise_for_status()
                    data = resp.json() or {}

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
        except Exception as exc:
            self.logger.warning(
                "SmartRecruiters fetch failed, returning empty",
                error=str(exc),
                company_id=self.company_id,
            )
            return opportunities

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
                        parts = [loc0.get("city"), loc0.get("country")]
                        location = ", ".join(x for x in parts if x) or None

            description_raw = None
            if isinstance(job_ad, dict):
                description_raw = job_ad.get("sections", {}).get("description", {}).get("text")

            return RawOpportunity(
                source=self.source,
                source_id=f"smartrecruiters:{post_id}",
                source_url=source_url,
                employer_url=source_url,
                title=title,
                company=self.company_id,
                company_url=None,
                description_raw=description_raw,
                location=location,
                is_remote=is_india_eligible_remote(location, description_raw),
                is_paid=True,
            )
        except Exception:
            return None