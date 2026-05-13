"""Integration tests for FastAPI endpoints using TestClient."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.seed import IRREGULAR_VERBS

_VERB_FORMS = {
    base: (past, participle) for base, past, participle, *_ in IRREGULAR_VERBS
}

# Prevent run_migrations from executing on SQLite
with patch("app.database.run_migrations"):
    from api.main import app


@pytest.fixture
def client():
    """Return a TestClient with an overridden DB dependency."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    test_session_factory = sessionmaker(bind=engine)
    test_session = test_session_factory()

    def override_get_db():
        try:
            yield test_session
        finally:
            pass

    app.dependency_overrides.clear()
    from app.database import get_db as original_get_db

    app.dependency_overrides[original_get_db] = override_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()
    test_session.close()


class TestQuizEndpoint:
    def test_get_quiz_verbs_empty(self, client):
        resp = client.get("/api/verbs/quiz?count=5")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_get_quiz_verbs_populated(self, client):
        # Insert a verb via the /api/seed endpoint
        resp = client.post("/api/seed")
        assert resp.status_code == 200

        resp = client.get("/api/verbs/quiz?count=5")
        data = resp.json()
        assert len(data) > 0
        # Should not expose correct answers
        assert "past" not in data[0]
        assert "participle" not in data[0]

    def test_get_quiz_verbs_default_count(self, client):
        resp = client.get("/api/verbs/quiz")
        assert resp.status_code == 200


def _first_verb_with_answer(client) -> tuple[dict, str, str]:
    """Fetch a verb from quiz and return (verb, correct_past, correct_participle)."""
    resp = client.get("/api/verbs/quiz?count=1")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    verb = data[0]
    past, participle = _VERB_FORMS[verb["base"]]
    return verb, past, participle


class TestAttemptsEndpoint:
    def test_submit_correct_answer(self, client):
        client.post("/api/seed")
        verb, past, participle = _first_verb_with_answer(client)
        resp = client.post(
            "/api/attempts",
            json={
                "verb_id": verb["id"],
                "past_given": past,
                "participle_given": participle,
            },
        )
        assert resp.status_code == 200
        assert resp.json()["correct"] is True

    def test_submit_wrong_answer(self, client):
        client.post("/api/seed")
        verb, _, _ = _first_verb_with_answer(client)
        resp = client.post(
            "/api/attempts",
            json={
                "verb_id": verb["id"],
                "past_given": "wrong",
                "participle_given": "wrong",
            },
        )
        assert resp.status_code == 200
        assert resp.json()["correct"] is False

    def test_submit_unknown_verb(self, client):
        resp = client.post(
            "/api/attempts",
            json={"verb_id": 9999, "past_given": "read", "participle_given": "read"},
        )
        assert resp.status_code == 404

    def test_submit_invalid_verb_id_zero(self, client):
        resp = client.post(
            "/api/attempts",
            json={"verb_id": 0, "past_given": "read", "participle_given": "read"},
        )
        assert resp.status_code == 422

    def test_submit_invalid_verb_id_negative(self, client):
        resp = client.post(
            "/api/attempts",
            json={"verb_id": -1, "past_given": "read", "participle_given": "read"},
        )
        assert resp.status_code == 422


class TestStatsEndpoint:
    def test_stats_empty(self, client):
        resp = client.get("/api/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["accuracy"] == 0.0

    def test_stats_with_attempts(self, client):
        client.post("/api/seed")
        verb, past, participle = _first_verb_with_answer(client)
        client.post(
            "/api/attempts",
            json={
                "verb_id": verb["id"],
                "past_given": past,
                "participle_given": participle,
            },
        )
        client.post(
            "/api/attempts",
            json={
                "verb_id": verb["id"],
                "past_given": "wrong",
                "participle_given": "wrong",
            },
        )
        resp = client.get("/api/stats")
        data = resp.json()
        assert data["total"] == 2
        assert data["correct"] == 1
        assert data["wrong"] == 1
        assert data["accuracy"] == 50.0

    def test_stats_hardest_verbs_typed(self, client):
        """Verify hardest_verbs returns typed objects, not plain dicts."""
        client.post("/api/seed")
        resp = client.get("/api/stats")
        data = resp.json()
        for entry in data["hardest_verbs"]:
            assert "verb" in entry
            assert "errors" in entry


class TestSeedEndpoint:
    def test_seed_returns_counts(self, client):
        resp = client.post("/api/seed")
        assert resp.status_code == 200
        data = resp.json()
        assert "added" in data
        assert "updated" in data

    def test_seed_idempotent(self, client):
        first = client.post("/api/seed").json()
        second = client.post("/api/seed").json()
        assert second["added"] == 0
        assert second["updated"] >= first["updated"]


class TestSpaFallback:
    def test_root_returns_html(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]
