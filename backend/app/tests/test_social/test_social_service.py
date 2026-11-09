"""Tests for social signal service."""

import sys
sys.path.insert(0, ".")

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from app.social.services.social_signal_service import SocialSignalService
from app.social.models.social_signal import SocialSignal


class FakeSession:
    """Minimal fake SQLAlchemy session for testing."""

    def __init__(self):
        self.added = []
        self.committed = False

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        self.committed = True

    def refresh(self, obj):
        pass

    def query(self, model):
        return FakeQuery(self, model)


class FakeQuery:
    def __init__(self, session, model):
        self.session = session
        self.model = model
        self._filters = []
        self._offset = 0
        self._limit = None

    def filter(self, *criterions):
        self._filters.extend(criterions)
        return self

    def filter_by(self, **kwargs):
        return self

    def offset(self, n):
        self._offset = n
        return self

    def limit(self, n):
        self._limit = n
        return self

    def all(self):
        return []

    def first(self):
        return None

    def count(self):
        return 0


class TestSocialSignalService:
    def setup_method(self):
        self.session = FakeSession()
        self.service = SocialSignalService(self.session)

    def test_process_raw_post_primary_signal(self):
        raw_post = {
            "post_id": "12345",
            "post_text": "We're hiring interns at Acme Corp! DM me your resume.",
            "post_url": "https://linkedin.com/posts/12345",
            "post_date": datetime(2024, 1, 15, tzinfo=timezone.utc),
            "author": "John Doe",
            "platform": "linkedin",
        }
        signal = self.service.process_raw_post(raw_post)

        assert signal.platform == "linkedin"
        assert signal.post_id == "12345"
        assert signal.company == "acme"
        assert signal.signal_type == "internship_post"
        assert signal.verification_status == "social_lead_not_verified"
        assert signal.confidence_score > 0.5
        assert signal.post_url == "https://linkedin.com/posts/12345"

    def test_process_raw_post_indirect_signal(self):
        raw_post = {
            "post_id": "67890",
            "post_text": "Excited to announce we recently raised $5M Series A!",
            "post_url": "https://twitter.com/posts/67890",
            "post_date": datetime(2024, 2, 1, tzinfo=timezone.utc),
            "author": "Founder",
            "platform": "x_twitter",
        }
        signal = self.service.process_raw_post(raw_post)

        assert signal.is_indirect_signal is True
        assert signal.verification_status == "indirect_signal"

    def test_process_batch(self):
        raw_posts = [
            {
                "post_id": "p1",
                "post_text": "Hiring interns at StartupXYZ",
                "post_url": "https://example.com/p1",
                "platform": "reddit",
            },
            {
                "post_id": "p2",
                "post_text": "Just having coffee",
                "post_url": "https://example.com/p2",
                "platform": "reddit",
            },
        ]
        signals = self.service.process_batch(raw_posts)
        assert len(signals) == 2
        assert signals[0].signal_type == "hiring_post"
        assert signals[1].signal_type == "unknown"

    def test_determine_verification_status_social_lead(self):
        status = self.service._determine_verification_status(
            post_text="We're hiring!",
            signal_type="hiring_post",
            is_indirect=False,
            company="test",
        )
        assert status == "social_lead_not_verified"

    def test_determine_verification_status_indirect(self):
        status = self.service._determine_verification_status(
            post_text="Raised funding",
            signal_type="indirect_signal",
            is_indirect=True,
            company=None,
        )
        assert status == "indirect_signal"

    def test_repo_add_called(self):
        raw_post = {
            "post_id": "p1",
            "post_text": "Hiring interns!",
            "post_url": "https://example.com/p1",
            "platform": "test",
        }
        self.service.process_raw_post(raw_post)
        assert len(self.session.added) == 1
        assert isinstance(self.session.added[0], SocialSignal)
        assert self.session.committed is True