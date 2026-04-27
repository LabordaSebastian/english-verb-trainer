"""Unit tests for quiz logic using an in-memory SQLite database."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Verb, UserAttempt
from app.quiz import get_verb_by_base, get_shuffled_verbs, validate_and_log, get_stats


# ─── fixtures ───────────────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def db():
    """In-memory SQLite session for fast, isolated tests (no Postgres needed)."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
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
    verb = Verb(base="learn", past="learned", participle="learned", past_alt="learnt", participle_alt="learnt")
    db.add(verb)
    db.commit()
    db.refresh(verb)
    return verb


# ─── Verb.check_answer ───────────────────────────────────────────────────────

class TestVerbCheckAnswer:
    def test_correct_lowercase(self, sample_verb):
        assert sample_verb.check_answer("read", "read") is True

    def test_correct_uppercase(self, sample_verb):
        assert sample_verb.check_answer("READ", "READ") is True

    def test_correct_mixed_case(self, sample_verb):
        assert sample_verb.check_answer("Read", "Read") is True

    def test_wrong_past(self, sample_verb):
        assert sample_verb.check_answer("readed", "read") is False

    def test_wrong_participle(self, sample_verb):
        assert sample_verb.check_answer("read", "readed") is False

    def test_both_wrong(self, sample_verb):
        assert sample_verb.check_answer("red", "redded") is False

    def test_alt_form_accepted(self, verb_with_alt):
        assert verb_with_alt.check_answer("learnt", "learnt") is True

    def test_primary_form_accepted(self, verb_with_alt):
        assert verb_with_alt.check_answer("learned", "learned") is True


# ─── get_random_verb ─────────────────────────────────────────────────────────

class TestGetVerbByBase:
    def test_returns_verb_by_base(self, db, sample_verb):
        result = get_verb_by_base(db, base="read")
        assert result is not None
        assert result.base == "read"

    def test_returns_none_for_unknown_verb(self, db):
        result = get_verb_by_base(db, base="xyzunknown")
        assert result is None


class TestGetShuffledVerbs:
    def test_returns_none_when_db_empty(self, db):
        result = get_shuffled_verbs(db)
        assert result == []

    def test_returns_all_verbs_when_populated(self, db, sample_verb):
        result = get_shuffled_verbs(db)
        assert len(result) == 1
        assert result[0].base == "read"

    def test_limit_respected(self, db):
        # Insert 3 verbs
        for base, past, part in [("go", "went", "gone"), ("do", "did", "done"), ("run", "ran", "run")]:
            db.add(Verb(base=base, past=past, participle=part))
        db.commit()
        result = get_shuffled_verbs(db, limit=2)
        assert len(result) == 2

    def test_no_duplicates_in_result(self, db):
        for base, past, part in [("go", "went", "gone"), ("do", "did", "done"), ("run", "ran", "run")]:
            db.add(Verb(base=base, past=past, participle=part))
        db.commit()
        result = get_shuffled_verbs(db)
        bases = [v.base for v in result]
        assert len(bases) == len(set(bases)), "Duplicate verbs found in shuffled list"


# ─── validate_and_log ────────────────────────────────────────────────────────

class TestValidateAndLog:
    def test_correct_answer_logged(self, db, sample_verb):
        result = validate_and_log(db, sample_verb, "read", "read")
        assert result is True
        attempt = db.query(UserAttempt).first()
        assert attempt is not None
        assert attempt.is_correct is True

    def test_wrong_answer_logged(self, db, sample_verb):
        result = validate_and_log(db, sample_verb, "readed", "readed")
        assert result is False
        attempt = db.query(UserAttempt).first()
        assert attempt.is_correct is False

    def test_multiple_attempts_recorded(self, db, sample_verb):
        validate_and_log(db, sample_verb, "read", "read")
        validate_and_log(db, sample_verb, "readed", "read")
        count = db.query(UserAttempt).count()
        assert count == 2


# ─── get_stats ───────────────────────────────────────────────────────────────

class TestGetStats:
    def test_empty_stats(self, db):
        stats = get_stats(db)
        assert stats["total"] == 0
        assert stats["correct"] == 0
        assert stats["accuracy"] == 0.0

    def test_stats_with_attempts(self, db, sample_verb):
        validate_and_log(db, sample_verb, "read", "read")   # correct
        validate_and_log(db, sample_verb, "readed", "read") # wrong
        stats = get_stats(db)
        assert stats["total"] == 2
        assert stats["correct"] == 1
        assert stats["wrong"] == 1
        assert stats["accuracy"] == 50.0

    def test_hardest_verbs_appears(self, db, sample_verb):
        validate_and_log(db, sample_verb, "wrong", "wrong")
        stats = get_stats(db)
        assert len(stats["hardest_verbs"]) == 1
        assert stats["hardest_verbs"][0]["verb"] == "read"
