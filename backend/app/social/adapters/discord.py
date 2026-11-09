"""Discord adapter — public community discovery.

NOTE: Discord offers a Community API and public channels. Guilds may be
invited or public. This adapter defines the contract for future
implementation with the official Discord API.
"""

from typing import Any

from app.social.adapters.base import BaseSocialAdapter
from app.social.utils.signal_detection import normalize


class DiscordAdapter(BaseSocialAdapter):
    platform = "discord"
    adapter_name = "discord"

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)
        self.bot_token = self.config.get("bot_token")
        self.guild_ids = self.config.get("guild_ids", [])

    async def discover(self) -> list[dict[str, Any]]:
        """Discover public Discord channel announcements.

        In MVP, this returns a template with a clear deprecation notice.
        Production: implement with Discord Community API for public channels.
        """
        self.logger.warning(
            "Discord adapter not yet implemented — requires bot token. "
            "Implementing with Discord Community API for public channels."
        )
        return []

    def _parse_discord_message(self, message: dict[str, Any]) -> dict[str, Any]:
        """Parse a Discord message into the internal raw post format."""
        return {
            "post_id": message.get("id"),
            "post_text": message.get("content") or message.get("message") or "",
            "post_url": f"https://discord.com/channels/{message.get('guild_id')}/{message.get('channel_id')}/{message.get('id')}",
            "post_date": message.get("timestamp"),
            "author": message.get("author", {}).get("username"),
            "author_role": message.get("author", {}).get("title"),
            "platform": "discord",
        }