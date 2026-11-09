"""Social hiring discovery adapters — one per platform.

Each adapter implements discover() -> list[SocialSignal] (or raw post data
that the service layer converts to SocialSignal).
"""

from app.social.adapters.base import BaseSocialAdapter
from app.social.adapters.company_blog import CompanyBlogAdapter
from app.social.adapters.discord import DiscordAdapter
from app.social.adapters.hacker_news import HackerNewsAdapter
from app.social.adapters.linkedin import LinkedInAdapter
from app.social.adapters.reddit import RedditAdapter
from app.social.adapters.startup_board import StartupBoardAdapter
from app.social.adapters.telegram import TelegramAdapter
from app.social.adapters.twitter_x import TwitterAdapter

__all__ = [
    "BaseSocialAdapter",
    "CompanyBlogAdapter",
    "DiscordAdapter",
    "HackerNewsAdapter",
    "LinkedInAdapter",
    "RedditAdapter",
    "StartupBoardAdapter",
    "TelegramAdapter",
    "TwitterAdapter",
]