"""Pytest configuration and fixtures."""

import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_internradar.db")

import pytest  # noqa: E402

from app.db.session import SessionLocal  # noqa: E402
from app.db.models.opportunity import Opportunity  # noqa: E402


@pytest.fixture
def db_session():
    """Provide an in-memory SQLite session for tests."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine("sqlite:///./test_internradar.db", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()