"""Tests for discovery filter functions."""

import pytest

from app.services.discovery_service import (
    description_is_relevant,
    is_india_eligible_remote,
    opportunity_passes_filters,
    title_is_internship,
)


class _Raw:
    def __init__(self, title, location=None, description_raw=None):
        self.title = title
        self.location = location
        self.description_raw = description_raw


@pytest.mark.parametrize(
    "title,expected",
    [
        ("Software Engineer Intern", True),
        ("Machine Learning Intern", True),
        ("Software Engineer", False),
        ("Senior Backend Developer", False),
        ("AI Engineer Internship", True),
    ],
)
def test_title_is_internship(title, expected):
    assert title_is_internship(title) == expected


@pytest.mark.parametrize(
    "description,expected",
    [
        ("We are hiring a software engineering intern for summer 2025", True),
        ("Looking for a full-time senior developer", False),
        ("Machine learning intern to work on LLM agents", True),
        (None, False),
        ("", False),
    ],
)
def test_description_is_relevant(description, expected):
    assert description_is_relevant(description) == expected


@pytest.mark.parametrize(
    "location,description,expected",
    [
        ("Remote, India", None, True),
        ("Remote, Worldwide", None, True),
        ("Bengaluru, India", None, True),
        ("Remote, US only", None, False),
        ("Remote, EU only", None, False),
        ("Onsite, Bengaluru", None, False),
        ("Remote", "Work from anywhere in India", True),
        ("Remote", "US-based remote only", False),
        ("Hybrid, India", "Remote eligible", True),
        ("Hybrid", "Onsite 3 days a week", False),
    ],
)
def test_is_india_eligible_remote(location, description, expected):
    assert is_india_eligible_remote(location, description) == expected


def test_opportunity_passes_filters_internship_title_india_remote():
    raw = _Raw("Software Engineer Intern", "Remote, India")
    assert opportunity_passes_filters(raw) is True


def test_opportunity_passes_filters_non_internship_irrelevant_desc():
    raw = _Raw("Senior Accountant", "Remote, India", "Manage financial records")
    assert opportunity_passes_filters(raw) is False


def test_opportunity_passes_filters_us_only_excluded():
    raw = _Raw("Software Engineer Intern", "Remote, US only")
    assert opportunity_passes_filters(raw) is False
