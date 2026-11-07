"""HTTP client for crawling public sources.

Provides a shared httpx client with retries, timeouts, user-agent rotation,
and respectful rate limiting. All requests are read-only GET/POST to public
endpoints. No authentication bypass, CAPTCHA solving, or access-control
circumvention is performed.
"""

import asyncio
import random
from typing import Any

import httpx
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)

# Rotating user-agents to be respectful and avoid fingerprinting blocks
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
    settings.USER_AGENT,
]


class CrawlError(Exception):
    """Raised when a crawl request fails after retries."""


class HttpClient:
    """Async HTTP client with retry logic and polite defaults."""

    def __init__(
        self,
        timeout: int | None = None,
        max_concurrent: int | None = None,
        user_agent: str | None = None,
    ):
        self.timeout = httpx.Timeout(timeout or settings.REQUEST_TIMEOUT)
        self.max_concurrent = max_concurrent or settings.MAX_CONCURRENT_REQUESTS
        self.user_agent = user_agent or random.choice(USER_AGENTS)
        self._semaphore = asyncio.Semaphore(self.max_concurrent)
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "HttpClient":
        self._client = httpx.AsyncClient(
            timeout=self.timeout,
            headers={"User-Agent": self.user_agent, "Accept": "text/html,application/json"},
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, *args: Any) -> None:
        if self._client:
            await self._client.aclose()

    async def get(self, url: str, **kwargs: Any) -> httpx.Response:
        assert self._client is not None, "HttpClient must be used as an async context manager"
        async with self._semaphore:
            last_error: Exception | None = None
            for attempt in range(3):
                try:
                    resp = await self._client.get(url, **kwargs)
                    if resp.status_code in (429, 502, 503, 504):
                        await asyncio.sleep(2 ** attempt + random.uniform(0, 1))
                        continue
                    return resp
                except (httpx.TimeoutException, httpx.ConnectError) as exc:
                    last_error = exc
                    await asyncio.sleep(2 ** attempt + random.uniform(0, 1))
            raise CrawlError(f"GET {url} failed: {last_error}")

    async def post(self, url: str, json: dict[str, Any] | None = None, **kwargs: Any) -> httpx.Response:
        assert self._client is not None, "HttpClient must be used as an async context manager"
        async with self._semaphore:
            last_error: Exception | None = None
            for attempt in range(3):
                try:
                    resp = await self._client.post(url, json=json, **kwargs)
                    if resp.status_code in (429, 502, 503, 504):
                        await asyncio.sleep(2 ** attempt + random.uniform(0, 1))
                        continue
                    return resp
                except (httpx.TimeoutException, httpx.ConnectError) as exc:
                    last_error = exc
                    await asyncio.sleep(2 ** attempt + random.uniform(0, 1))
            raise CrawlError(f"POST {url} failed: {last_error}")