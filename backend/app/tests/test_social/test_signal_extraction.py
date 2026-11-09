"""Tests for signal extraction utilities."""

import sys
sys.path.insert(0, ".")

import pytest

from app.social.services.signal_extraction import (
    detect_company,
    detect_author,
    extract_roles,
    extract_skills,
    extract_stipend,
    extract_remote,
    extract_contact_instructions,
    is_indirect_signal,
    compute_confidence,
)


class TestComputeConfidence:
    def test_baseline(self):
        score = compute_confidence(
            post_text="test",
            primary_match=False,
            company_detected=False,
            is_indirect=False,
            has_contact=False,
        )
        assert score == 0.5

    def test_primary_match_boosts(self):
        score = compute_confidence(
            post_text="test",
            primary_match=True,
            company_detected=False,
            is_indirect=False,
            has_contact=False,
        )
        assert score == 0.8

    def test_indirect_reduces(self):
        score = compute_confidence(
            post_text="test",
            primary_match=True,
            company_detected=True,
            is_indirect=True,
            has_contact=True,
        )
        assert score == 0.7

    def test_clamped_to_range(self):
        score = compute_confidence(
            post_text="test",
            primary_match=True,
            company_detected=True,
            is_indirect=False,
            has_contact=True,
        )
        assert 0.0 <= score <= 1.0


class TestIsIndirectSignal:
    def test_funding_phrase(self):
        assert is_indirect_signal("Recently raised $5M Series A") is True

    def test_new_team_phrase(self):
        assert is_indirect_signal("Building a new engineering team") is True

    def test_not_indirect(self):
        assert is_indirect_signal("We're hiring interns!") is False