"""X/Twitter adapter — public post discovery.

NOTE: X/Twitter's public API (v2) requires a developer account and
may have rate limits. This adapter is a template that defines the
contract for future implementation with the official API.
"""

from typing import Any

from app.social.adapters.base import BaseSocialAdapter
from app.social.utils.signal_detection import normalize


class TwitterAdapter(BaseSocialAdapter):
    platform = "x_twitter"
    adapter_name = "twitter_x"

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)
        self.bearer_token = self.config.get("bearer_token")
        self.company_names = self.config.get("company_names", [])

    async def discover(self) -> list[dict[str, Any]]:
        """Discover public posts from X/Twitter.

        In MVP, this returns a template with a clear deprecation notice.
        Production: implement with X/Twitter API v2, academic track,
        or authorized public feed.
        """
        self.logger.warning(
            "X/Twitter adapter not yet implemented — requires developer API access. "
            "Implementing with X/Twitter API v2 or authorized public feed."
        )
        return []

    def _parse_tweet(self, tweet: dict[str, Any]) -> dict[str, Any]:
        """Parse a tweet into the internal raw post format."""
        return {
            "post_id": tweet.get("id") or tweet.get("tweet_id") or "",
            "post_text": tweet.get("text") or tweet.get("content") or "",
            "post_url": tweet.get("url") or tweet.get("permalink") or "",
            "post_date": tweet.get("created_at") or tweet.get("published_at"),
            "author": tweet.get("author_id") or tweet.get("author_name"),
            "author_role": tweet.get("author_role"),
            "platform": "x_twitter",
        }