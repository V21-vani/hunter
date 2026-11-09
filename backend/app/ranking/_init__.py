"""Ranking module for internship opportunities.

Provides stipend ranking tiers and recency ranking logic.
"""

from app.ranking.stipend import stipend_tier, is_stipend_acceptable
from app.ranking.recency import is_recent, is_recruitment_stale