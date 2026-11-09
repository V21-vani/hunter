"""Tests for signal detection utilities."""

import sys
sys.path.insert(0, ".")

import pytest

from app.social.utils.signal_detection import (
    normalize,
    detect_signal_type,
    detect_company,
    detect_author,
    extract_roles,
    extract_skills,
    extract_stipend,
    extract_remote,
    extract_contact_instructions,
    PRIMARY_HIRING_PHRASES,
    INDIRECT_SIGNAL_PHRASES,
)


class TestNormalize:
    def test_lowercase(self):
        assert normalize("HELLO World") == "hello world"

    def test_collapse_whitespace(self):
        assert normalize("hello   world") == "hello world"

    def test_strip_punctuation(self):
        assert normalize("hello, world!") == "hello world"

    def test_empty(self):
        assert normalize("") == ""
        assert normalize(None) == ""


class TestDetectSignalType:
    def test_internship_post(self):
        assert detect_signal_type("We're hiring interns!") == "internship_post"
        assert detect_signal_type("Looking for engineering interns") == "internship_post"

    def test_hiring_post(self):
        assert detect_signal_type("Building our engineering team") == "engineering_follower_post"
        assert detect_signal_type("Hiring for our team") == "team_hiring_post"
        assert detect_signal_type("We're hiring") == "hiring_post"

    def test_indirect_signal(self):
        assert detect_signal_type("Recently raised funding") == "indirect_signal"
        assert detect_signal_type("New product launch") == "indirect_signal"

    def test_unknown(self):
        assert detect_signal_type("Just having lunch") == "unknown"


class TestDetectCompany:
    def test_at_pattern(self):
        assert detect_company("We're hiring at Acme Corp") == "acme"

    def test_from_pattern(self):
        assert detect_company("Job from StartupXYZ") == "startupxyz"

    def test_url_pattern(self):
        assert detect_company("Visit https://example.com/jobs") == "example"

    def test_no_company(self):
        assert detect_company("Just a random post") is None


class TestDetectAuthor:
    def test_posted_by(self):
        assert detect_author("Posted by John Doe") == "john doe"

    def test_from(self):
        assert detect_author("From Jane Smith") == "jane smith"

    def test_explicit_author(self):
        assert detect_author("text", author="Alice") == "alice"


class TestExtractRoles:
    def test_engineer(self):
        assert extract_roles("Looking for a software engineer") == "engineer"

    def test_intern(self):
        assert extract_roles("Hiring interns for summer") == "intern"

    def test_no_role(self):
        assert extract_roles("Just a random post") is None


class TestExtractSkills:
    def test_python_js(self):
        skills = extract_skills("Python and JavaScript developer needed")
        assert "python" in skills
        assert "javascript" in skills

    def test_empty(self):
        assert extract_skills("No skills mentioned") == []


class TestExtractStipend:
    def test_lpa(self):
        assert extract_stipend("Stipend of 15 LPA") == "15 lpa"

    def test_dollar_month(self):
        assert extract_stipend("$2000 per month") == "$2000 per month"


class TestExtractRemote:
    def test_remote(self):
        assert extract_remote("Fully remote position") == "remote"

    def test_onsite(self):
        assert extract_remote("Onsite in Bengaluru") == "onsite"

    def test_hybrid(self):
        assert extract_remote("Hybrid work model") == "hybrid"

    def test_none(self):
        assert extract_remote("No location info") is None


class TestExtractContactInstructions:
    def test_dm_me(self):
        result = extract_contact_instructions("DM me your resume")
        assert result is not None
        assert "dm me" in result.lower()

    def test_no_contact(self):
        assert extract_contact_instructions("Just hiring") is None


class TestPhraseLists:
    def test_primary_phrases_nonempty(self):
        assert len(PRIMARY_HIRING_PHRASES) > 15

    def test_indirect_phrases_nonempty(self):
        assert len(INDIRECT_SIGNAL_PHRASES) > 10