"""Company blog / founder blog adapter — public blog post discovery.

NOTE: Many company blogs are publicly accessible via RSS feeds or sitemaps.
This adapter defines the contract for fetching blog posts and extracting
hiring signals.
"""

from typing import Any

from app.social.adapters.base import BaseSocialAdapter
from app.social.utils.signal_detection import normalize


class CompanyBlogAdapter(BaseSocialAdapter):
    platform = "company_blog"
    adapter_name = "company_blog"

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)
        self.feed_urls = self.config.get("feed_urls", [])
        self.companies = self.config.get("companies", [])

    async def discover(self) -> list[dict[str, Any]]:
        """Discover public blog posts from company blogs via RSS feeds.

        In MVP, this returns a template with a clear deprecation notice.
        Production: implement with RSS feed parsing (feedparser or similar).
        """
        self.logger.warning(
            "Company blog adapter not yet implemented — requires RSS feed URLs. "
            "Implementing with RSS/Atom feed parsing."
        )
        return []

    def _parse_blog_post(self, post: dict[str, Any]) -> dict[str, Any]:
        """Parse a blog post into the internal raw post format."""
        return {
            "post_id": post.get("id") or post.get("url") or post.get("slug") or "",
            "post_text": post.get("title") or "" + " " + post.get("content") or "",
            "post_url": post.get("url") or post.get("link") or "",
            "post_date": post.get("date") or post.get("published") or post.get("updated") or "",
            "author": post.get("author") or post.get("author_name") or "",
            "author_role": "founder" if post.get("author_role") == "founder" else None,
            "platform": "company_blog",
        }