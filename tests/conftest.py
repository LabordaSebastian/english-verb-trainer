"""Shared test fixtures and configuration."""

import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import Verb

# ─── migrations mock (SQLite incompatible) ───────────────────────────────────


@pytest.fixture(scope="session", autouse=True)
def _mock_migrations():
    with patch("app.database.run_migrations"):
        yield


# ─── DB fixtures ─────────────────────────────────────────────────────────────


@pytest.fixture(scope="function")
def db():
    """In-memory SQLite session for fast, isolated tests."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_verb(db):
    """Insert the verb READ into the test DB."""
    verb = Verb(base="read", past="read", participle="read")
    db.add(verb)
    db.commit()
    db.refresh(verb)
    return verb


@pytest.fixture
def verb_with_alt(db):
    """Insert LEARN with alternative forms (learned / learnt)."""
    verb = Verb(
        base="learn",
        past="learned",
        participle="learned",
        past_alt="learnt",
        participle_alt="learnt",
    )
    db.add(verb)
    db.commit()
    db.refresh(verb)
    return verb


@pytest.fixture
def three_verbs(db):
    """Insert three distinct verbs (go, do, run)."""
    verbs = [
        Verb(base="go", past="went", participle="gone"),
        Verb(base="do", past="did", participle="done"),
        Verb(base="run", past="ran", participle="run"),
    ]
    for v in verbs:
        db.add(v)
    db.commit()
    return verbs
