"""Startup community boards adapter — public hiring board discovery.

NOTE: Startup boards (e.g., Y Combinator's Work at a Startup, AngelList,
productboard's hiring board, etc.) are public board aggregators.
This adapter defines the contract for future implementation.
"""

from typing import Any

from app.social.adapters.base import BaseSocialAdapter
from app.social.utils.signal_detection import normalize


class StartupBoardAdapter(BaseSocialAdapter):
    platform = "startup_board"
    adapter_name = "startup_board"

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)
        self.boards = self.config.get("boards", [])

    async def discover(self) -> list[dict[str, Any]]:
        """Discover public startup hiring board posts.

        In MVP, this returns a template with a clear deprecation notice.
        Production: implement with specific startup board APIs or scrapers.
        """
        self.logger.warning(
            "Startup board adapter not yet implemented — requires board URLs. "
            "Implementing with public startup hiring board scraping."
        )
        return []

    def _parse_board_post(self, post: dict[str, Any]) -> dict[str, Any]:
        """Parse a board post into the internal raw post format."""
        return {
            "post_id": post.get("id") or post.get("slug") or "",
            "post_text": post.get("title") or "" + " " + post.get("body") or "",
            "post_url": post.get("url") or post.get("link") or "",
            "post_date": post.get("date") or post.get("created_at") or "",
            "author": post.get("author") or post.get("user") or "",
            "author_role": post.get("role") or None,
            "platform": "startup_board",
        }