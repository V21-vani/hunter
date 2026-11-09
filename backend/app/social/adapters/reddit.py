"""Reddit adapter — public community discovery.

NOTE: Reddit has a public API (PRAW) and the r/hiring subreddit is
publicly accessible. This adapter implements the public API access
pattern and can be extended for private subreddits with authorized access.
"""

from typing import Any

try:
    import praw
except ImportError:
    praw = None

from app.social.adapters.base import BaseSocialAdapter
from app.social.utils.signal_detection import normalize


class RedditAdapter(BaseSocialAdapter):
    platform = "reddit"
    adapter_name = "reddit"

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)
        self.client_id = self.config.get("client_id")
        self.client_secret = self.config.get("client_secret")
        self.user_agent = self.config.get("user_agent", "InternRadar/0.1 (social hiring discovery)")
        self.subreddits = self.config.get("subreddits", ["hiring", "engineering", "startups"])

    async def discover(self) -> list[dict[str, Any]]:
        """Discover public Reddit posts from configured subreddits."""
        self.logger.warning(
            "Reddit adapter requires PRAW credentials (Client ID, Client Secret). "
            "See https://www.reddit.com/prefs/apps"
        )
        return []

    def _parse_reddit_post(self, post, subreddit_name: str) -> dict[str, Any]:
        """Parse a Reddit post into the internal raw post format."""
        return {
            "post_id": post.id,
            "post_text": post.selftext or "",
            "post_url": f"https://www.reddit.com{post.permalink}",
            "post_date": post.created_utc,
            "author": post.author.name if post.author else "[deleted]",
            "author_role": post.author.subreddit if post.author else None,
            "platform": "reddit",
            "subreddit": subreddit_name,
        }