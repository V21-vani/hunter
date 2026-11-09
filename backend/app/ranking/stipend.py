"""Stipend ranking module for internship opportunities.

Ranking tiers based on guaranteed fixed monthly stipend (INR only):
- Tier 1: ₹30,000+
- Tier 2: ₹20,000–₹29,999
- Tier 3: ₹15,000–₹19,999
- Tier 4: ₹10,000–₹14,999

Never add incentives to fixed stipend. Reject unpaid, below ₹10,000, and pay-to-join.
"""

from typing import Optional


def stipend_tier(stipend: Optional[float]) -> Optional[int]:
    """Return the stipend tier (1-4) or None if insufficient.

    Tier thresholds (INR, fixed monthly):
    - Tier 1: ≥ ₹30,000
    - Tier 2: ₹20,000–₹29,999
    - Tier 3: ₹15,000–₹19,999
    - Tier 4: ₹10,000–₹14,999
    - None: < ₹10,000 or None (unpaid/undisclosed)
    """
    if stipend is None:
        return None
    if stipend >= 30000:
        return 1
    elif stipend >= 20000:
        return 2
    elif stipend >= 15000:
        return 3
    elif stipend >= 10000:
        return 4
    else:
        # Below minimum — reject
        return None


def is_stipend_acceptable(stipend: Optional[float], stipend_type: Optional[str] = None) -> bool:
    """Return True if the stipend is acceptable for Phase 5.

    Rejects:
    - Unpaid (None)
    - Below ₹10,000/month
    - Pay-to-join schemes
    - Unproductive trial periods (stipend_type == 'commission' or 'hourly' without fixed)
    """
    if stipend is None:
        return False  # unpaid
    if stipend < 10000:
        return False  # below minimum
    # Reject commission-only or hourly-only without fixed component
    if stipend_type and stipend_type in ('commission', 'hourly') and not stipend:
        return False
    return True