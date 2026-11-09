"""LinkedIn adapter — public post discovery.

NOTE: LinkedIn restricts public API access to authenticated, authorised
providers. This adapter is a template that defines the contract and can
be populated later with an authorised provider (e.g., LinkedIn Official
API, certified partner, or authenticated public feed).

Access restrictions applied:
- Only public company posts, founder announcements, and recruiter posts
- No private profiles, groups, or restricted content
- No login bypass or content scraping behind auth walls
"""

from typing import Any

from app.social.adapters.base import BaseSocialAdapter
from app.social.utils.signal_detection import normalize


class LinkedInAdapter(BaseSocialAdapter):
    platform = "linkedin"
    adapter_name = "linkedin"

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)
        self.access_token = self.config.get("access_token")
        self.companies = self.config.get("companies", [])

    async def discover(self) -> list[dict[str, Any]]:
        """Discover public posts from linkedin.

        In MVP, this returns a template with a clear deprecation notice.
        Production: implement with LinkedIn Official API or authorized
        public feed provider.
        """
        self.logger.warning(
            "LinkedIn adapter not yet implemented — requires authorized API access. "
            "Implementing with official LinkedIn API or certified partner."
        )
        return []

    def _parse_public_post(self, post: dict[str, Any]) -> dict[str, Any]:
        """Parse a LinkedIn public post into the internal raw post format."""
        return {
            "post_id": post.get("id") or post.get("postId") or post.get("uuid") or "",
            "post_text": post.get("text") or post.get("content") or "",
            "post_url": post.get("share_url") or post.get("url") or "",
            "post_date": post.get("datetime") or post.get("created_at"),
            "author": post.get("author") or post.get("author_name"),
            "author_role": post.get("author_role"),
            "platform": "linkedin",
        }