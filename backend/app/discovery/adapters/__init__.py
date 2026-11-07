"""Source adapters — one per hiring source.

Each adapter implements discover() -> list[RawOpportunity].
Adapters are independent and can be added without modifying the engine.
"""

from app.discovery.adapters.base import BaseAdapter
from app.discovery.adapters.greenhouse import GreenhouseAdapter
from app.discovery.adapters.lever import LeverAdapter
from app.discovery.adapters.ashby import AshbyAdapter
from app.discovery.adapters.smartrecruiters import SmartRecruitersAdapter
from app.discovery.adapters.workday import WorkdayAdapter
from app.discovery.adapters.company_page import CompanyCareerPageAdapter

__all__ = [
    "BaseAdapter",
    "GreenhouseAdapter",
    "LeverAdapter",
    "AshbyAdapter",
    "SmartRecruitersAdapter",
    "WorkdayAdapter",
    "CompanyCareerPageAdapter",
]