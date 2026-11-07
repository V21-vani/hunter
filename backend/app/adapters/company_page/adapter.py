"""Company career page adapter.

Fetches an employer-owned careers page and extracts JobPosting schema.org
objects from JSON-LD, falling back to heuristic link detection when no
structured data is present. This supports small startups and overlooked
companies that do not use a major ATS.
"""

from typing import Any

from app.adapters.base import BaseAdapter, RawOpportunity
from app.crawling.bs4_parser import extract_jobposting_from_json_ld
from app.crawling.http_client import CrawlError, HttpClient


class CompanyCareerPageAdapter(BaseAdapter):
    source = "company_page"
    adapter_name = "company_page"

    def __init__(
        self,
        company_name: str,
        careers_url: str,
        company_url: str | None = None,
    ):
        self.company_name = company_name
        self.careers_url = careers_url
        self.company_url = company_url

    async def discover(self) -> list[RawOpportunity]:
        opportunities: list[RawOpportunity] = []
        async with HttpClient() as client:
            try:
                resp = await client.get(self.careers_url)
            except CrawlError as exc:
                raise CrawlError(f"Company page {self.company_name}: {exc}")

            if resp.status_code != 200:
                raise CrawlError(
                    f"Company page {self.company_name}: HTTP {resp.status_code}"
                )

            html = resp.text

        jobs = extract_jobposting_from_json_ld(html)
        if jobs:
            for job in jobs:
                opp = self._parse_json_ld(job)
                if opp:
                    opportunities.append(opp)
        else:
            # Fallback: look for job-like links
            links = self._extract_job_links(html)
            for url, title in links:
                opportunities.append(
                    RawOpportunity(
                        source=self.source,
                        source_id=f"company_page:{hash(url)}",
                        source_url=url,
                        employer_url=self.company_url or self.careers_url,
                        title=title or "Job Opening",
                        company=self.company_name,
                        company_url=self.company_url,
                        description_raw=None,
                        location=None,
                        is_remote=False,
                        is_paid=False,
                        application_url=url,
                        raw_payload={"careers_url": self.careers_url},
                    )
                )

        return opportunities

    def _parse_json_ld(self, job: dict[str, Any]) -> RawOpportunity | None:
        try:
            title = job.get("title") or job.get("name") or ""
            if not title:
                return None

            post_id = job.get("identifier") or job.get("url") or ""
            if not post_id:
                post_id = f"{self.company_name}:{title}"

            source_url = job.get("url") or self.careers_url
            employer_url = self.company_url or self.careers_url

            hiring_org = job.get("hiringOrganization") or {}
            if isinstance(hiring_org, dict):
                company = hiring_org.get("name") or self.company_name
            else:
                company = self.company_name

            location = None
            job_location = job.get("jobLocation") or {}
            if isinstance(job_location, dict):
                address = job_location.get("address") or {}
                if isinstance(address, dict):
                    parts = [
                        address.get("addressLocality"),
                        address.get("addressRegion"),
                        address.get("addressCountry"),
                    ]
                    location = ", ".join(p for p in parts if p) or None
            if not location:
                location = job.get("jobLocation") if isinstance(job.get("jobLocation"), str) else None

            description_raw = job.get("description") or None
            date_posted = job.get("datePosted")

            return RawOpportunity(
                source=self.source,
                source_id=f"company_page:{post_id}",
                source_url=source_url,
                employer_url=employer_url,
                title=title,
                company=company,
                company_url=self.company_url,
                description_raw=description_raw,
                location=location,
                is_remote=self._looks_remote(location, description_raw),
                is_paid=False,
                application_url=job.get("url") or source_url,
                raw_payload=job,
            )
        except Exception:
            return None

    def _extract_job_links(self, html: str) -> list[tuple[str, str]]:
        from app.crawling.bs4_parser import find_links

        links = find_links(html, self.careers_url, keyword="job")
        seen: set[str] = set()
        result: list[tuple[str, str]] = []
        for url in links:
            if url in seen:
                continue
            seen.add(url)
            result.append((url, ""))
        return result

    @staticmethod
    def _looks_remote(location: str | None, description: str | None) -> bool:
        text = " ".join(filter(None, [location or "", description or ""])).lower()
        return any(m in text for m in ["india", "remote", "worldwide", "anywhere"])