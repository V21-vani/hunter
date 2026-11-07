"""Tests for source adapters using fixture data."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.adapters.greenhouse.adapter import GreenhouseAdapter
from app.adapters.lever.adapter import LeverAdapter
from app.adapters.ashby.adapter import AshbyAdapter
from app.adapters.smartrecruiters.adapter import SmartRecruitersAdapter
from app.adapters.workday.adapter import WorkdayAdapter
from app.adapters.company_page.adapter import CompanyCareerPageAdapter
from app.crawling.bs4_parser import extract_jobposting_from_json_ld
from app.crawling.http_client import HttpClient


GREENHOUSE_PAYLOAD = {
    "jobs": [
        {
            "id": 123456,
            "title": "Software Engineer Intern",
            "absolute_url": "https://boards.greenhouse.io/acme/jobs/123456",
            "location": {"name": "Remote, India"},
            "description": "Build scalable backend services.",
            "updated_at": "2024-01-15T10:00:00Z",
        },
        {
            "id": 789012,
            "title": "Senior Product Manager",
            "absolute_url": "https://boards.greenhouse.io/acme/jobs/789012",
            "location": {"name": "San Francisco, CA"},
            "description": "Lead product strategy.",
            "updated_at": "2024-01-10T10:00:00Z",
        },
    ]
}

LEVER_PAYLOAD = [
    {
        "id": "abc123",
        "text": "Machine Learning Intern",
        "applyUrl": "https://jobs.lever.co/acme/abc123",
        "categories": {"location": "Remote, India"},
        "description": "Work on LLM agents and retrieval systems.",
        "createdAt": "2024-02-01T00:00:00Z",
    }
]

ASHBY_PAYLOAD = {
    "jobPostingBoard": {
        "jobPostings": [
            {
                "id": "ashby-1",
                "title": "AI Engineer Intern",
                "jobUrl": "https://jobs.ashbyhq.com/acme/ashby-1",
                "location": {"city": "Bengaluru", "country": "India"},
                "descriptionHtml": "<p>Build AI agents.</p>",
            }
        ]
    }
}

def _mock_json(payload):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json = MagicMock(return_value=payload)
    mock_resp.text = ""
    return mock_resp


def test_greenhouse_adapter_parser_filters():
    adapter = GreenhouseAdapter(board_id="acme", company_name="Acme Inc")
    parsed = [adapter._parse_job(j) for j in GREENHOUSE_PAYLOAD["jobs"]]
    parsed = [p for p in parsed if p is not None]
    from app.services.discovery_service import opportunity_passes_filters
    filtered = [p for p in parsed if opportunity_passes_filters(p)]
    titles = [p.title for p in filtered]
    assert "Software Engineer Intern" in titles
    assert "Senior Product Manager" not in titles
    assert parsed[0].source_id == "greenhouse:123456"
    assert parsed[0].company == "Acme Inc"


def test_lever_adapter_parser():
    adapter = LeverAdapter(company="acme")
    parsed = [adapter._parse_posting(p) for p in LEVER_PAYLOAD]
    parsed = [p for p in parsed if p is not None]
    assert len(parsed) == 1
    assert parsed[0].title == "Machine Learning Intern"
    assert parsed[0].source_id == "lever:abc123"


def test_ashby_adapter_parser():
    adapter = AshbyAdapter(company="acme")
    postings = ASHBY_PAYLOAD["jobPostingBoard"]["jobPostings"]
    parsed = [adapter._parse_posting(p) for p in postings]
    parsed = [p for p in parsed if p is not None]
    assert len(parsed) == 1
    assert parsed[0].title == "AI Engineer Intern"
    assert parsed[0].source_id == "ashby:ashby-1"

SMARTRECRUITERS_PAYLOAD = {
    "content": [
        {
            "id": "sr-1",
            "name": "DevOps Intern",
            "ref": {"absoluteUri": "https://careers.smartrecruiters.com/acme/sr-1"},
            "jobAd": {
                "locations": [{"city": "Remote", "country": "India"}],
                "sections": {"description": {"text": "Support cloud infrastructure."}},
            },
        }
    ],
    "totalFound": 1,
}

WORKDAY_PAYLOAD = {
    "jobPostings": [
        {
            "id": "wd-1",
            "title": "Cloud Engineer Intern",
            "externalPath": "/acme/jobs/Cloud-Engineer-Intern-1",
            "locations": [{"city": "Remote", "country": "India"}],
            "postedOn": "2024-03-01",
        }
    ],
    "total": 1,
}

COMPANY_PAGE_HTML = """
<html><body>
<script type="application/ld+json">
{"@type": "JobPosting", "title": "Frontend Engineer Intern",
 "identifier": "cp-1", "url": "https://example.com/jobs/frontend-intern",
 "hiringOrganization": {"name": "Example Corp"},
 "jobLocation": {"address": {"addressLocality": "Remote", "addressCountry": "India"}},
 "description": "Build React components.",
 "datePosted": "2024-04-01"}
</script>
</body></html>
"""


def test_smartrecruiters_adapter_parser():
    adapter = SmartRecruitersAdapter(company_id="acme")
    parsed = [adapter._parse_posting(p) for p in SMARTRECRUITERS_PAYLOAD["content"]]
    parsed = [p for p in parsed if p is not None]
    assert len(parsed) == 1
    assert parsed[0].title == "DevOps Intern"
    assert parsed[0].source_id == "smartrecruiters:sr-1"


def test_workday_adapter_parser():
    adapter = WorkdayAdapter(tenant="acme", site="careers", company_name="Acme Inc")
    parsed = [adapter._parse_posting(p) for p in WORKDAY_PAYLOAD["jobPostings"]]
    parsed = [p for p in parsed if p is not None]
    assert len(parsed) == 1
    assert parsed[0].title == "Cloud Engineer Intern"
    assert parsed[0].source_id == "workday:wd-1"
    assert "wd5.myworkdayjobs.com" in parsed[0].source_url


def test_company_page_adapter_json_ld():
    adapter = CompanyCareerPageAdapter(
        company_name="Example Corp",
        careers_url="https://example.com/careers",
        company_url="https://example.com",
    )
    jobs = extract_jobposting_from_json_ld(COMPANY_PAGE_HTML)
    assert len(jobs) == 1
    opp = adapter._parse_json_ld(jobs[0])
    assert opp is not None
    assert opp.title == "Frontend Engineer Intern"
    assert opp.source_id.startswith("company_page:")
    assert "India" in (opp.location or "")


@pytest.mark.asyncio
async def test_lever_async_discover():
    adapter = LeverAdapter(company="acme")
    with patch("app.adapters.lever.adapter.HttpClient") as MockClient:
        instance = MockClient.return_value.__aenter__.return_value
        instance.get = AsyncMock(return_value=_mock_json(LEVER_PAYLOAD))
        result = await adapter.discover()
        assert len(result) == 1
        assert result[0].title == "Machine Learning Intern"
        assert result[0].source_id == "lever:abc123"


@pytest.mark.asyncio
async def test_ashby_async_discover():
    adapter = AshbyAdapter(company="acme")
    with patch("app.adapters.ashby.adapter.HttpClient") as MockClient:
        instance = MockClient.return_value.__aenter__.return_value
        instance.post = AsyncMock(return_value=_mock_json(ASHBY_PAYLOAD))
        result = await adapter.discover()
        assert len(result) == 1
        assert result[0].title == "AI Engineer Intern"
