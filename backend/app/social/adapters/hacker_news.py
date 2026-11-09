"""Hacker News adapter — public hiring threads discovery.

Hacker News is a public web forum with an open API. This adapter
implements the public API access pattern for discovering hiring
threads (Ask HN, Show HN, job postings).
"""

from typing import Any

import requests

from app.social.adapters.base import BaseSocialAdapter
from app.social.utils.signal_detection import normalize


class HackerNewsAdapter(BaseSocialAdapter):
    platform = "hacker_news"
    adapter_name = "hacker_news"

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)
        self.api_url = "https://hacker-news.firebaseio.com/v0"
        self.max_items = config.get("max_items", 100) if config else 100

    async def discover(self) -> list[dict[str, Any]]:
        """Discover public HN threads mentioning hiring."""
        self.logger.warning(
            "Hacker News adapter requires HN API (public, no auth). "
            "Implementing with HN API /v0."
        )
        return await self._fetch_hn_threads()

    async def _fetch_hn_threads(self) -> list[dict[str, Any]]:
        """Fetch HN stories and filter for hiring mentions."""
        results = []
        # Fetch top stories from HN API
        try:
            resp = requests.get(f"{self.api_url}/topstories.json", timeout=30)
            resp.raise_for_status()
            top_story_ids = resp.json()[:self.max_items]

            for story_id in top_story_ids:
                story_resp = requests.get(f"{self.api_url}/item/{story_id}.json", timeout=30)
                story_resp.raise_for_status()
                story = story_resp.json()

                if story.get("type") != "story":
                    continue

                title = story.get("title") or ""
                text = title  # HN titles are the main content
                content = story.get("content") or ""
                if content:
                    text += " " + content

                if self._has_hiring_signal(text):
                    results.append(self._parse_hn_story(story))
        except Exception as exc:
            self.logger.warning("Hacker News fetch failed", error=str(exc))
        return results

    def _has_hiring_signal(self, text: str) -> bool:
        """Check if a HN story contains hiring signal phrases."""
        normalized = normalize(text)
        hiring_phrases = [
            "hiring", "we're hiring", "we are hiring", "intern", "student",
            "welcoming candidates", "join our team", "we're looking for",
            "seeking", "open to", "freshers", "new grads",
        ]
        return any(phrase in normalized for phrase in hiring_phrases)

    def _parse_hn_story(self, story: dict[str, Any]) -> dict[str, Any]:
        """Parse an HN story into the internal raw post format."""
        return {
            "post_id": str(story.get("id")),
            "post_text": story.get("title") or "",
            "post_url": f"https://news.ycombinator.com/item?id={story.get('id')}",
            "post_date": story.get("time"),
            "author": story.get("by") or story.get("author"),
            "author_role": "hacker" if story.get("by") else None,
            "platform": "hacker_news",
            "is_indirect": False,
        }