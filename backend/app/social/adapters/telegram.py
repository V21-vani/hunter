"""Telegram adapter — public channel discovery.

NOTE: Telegram requires a bot token for API access. Public channels
can be accessed via the Bot API or by reading public channel messages.
This adapter defines the contract for future implementation.
"""

from typing import Any

from app.social.adapters.base import BaseSocialAdapter
from app.social.utils.signal_detection import normalize


class TelegramAdapter(BaseSocialAdapter):
    platform = "telegram"
    adapter_name = "telegram"

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)
        self.bot_token = self.config.get("bot_token")
        self.channels = self.config.get("channels", [])

    async def discover(self) -> list[dict[str, Any]]:
        """Discover public Telegram channel posts.

        In MVP, this returns a template with a clear deprecation notice.
        Production: implement with Telegram Bot API for public channels.
        """
        self.logger.warning(
            "Telegram adapter not yet implemented — requires bot token. "
            "Implementing with Telegram Bot API for public channels."
        )
        return []

    def _parse_telegram_message(self, message: dict[str, Any]) -> dict[str, Any]:
        """Parse a Telegram message into the internal raw post format."""
        return {
            "post_id": f"tg_{message.get('message_id', '')}",
            "post_text": message.get("text") or message.get("message") or "",
            "post_url": f"https://t.me/{message.get('chat', {}).get('username', '')}/{message.get('message_id', '')}",
            "post_date": message.get("date"),
            "author": message.get("from", {}).get("username") or message.get("from", {}).get("first_name"),
            "author_role": message.get("from", {}).get("title"),
            "platform": "telegram",
        }