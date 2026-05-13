"""Tests for Typer CLI commands using CliRunner."""

from unittest.mock import patch

import pytest
from sqlalchemy.pool import StaticPool
from typer.testing import CliRunner

from app.database import Base
from app.models import Verb

runner = CliRunner()


def _init_test_db(db_session):
    """Populate an in-memory SQLite with the seed data."""
    Base.metadata.create_all(bind=db_session.bind)
    verbs_data = [
        Verb(base="read", past="read", participle="read"),
        Verb(base="go", past="went", participle="gone"),
        Verb(base="do", past="did", participle="done"),
    ]
    for v in verbs_data:
        db_session.add(v)
    db_session.commit()


class TestSeedCommand:
    def test_seed_success(self):
        with (
            patch("main._init_db"),
            patch("main.SessionLocal") as mock_session_local,
        ):
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            from sqlalchemy.pool import StaticPool

            engine = create_engine(
                "sqlite:///:memory:",
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )
            Base.metadata.create_all(bind=engine)
            session_factory = sessionmaker(bind=engine)
            session = session_factory()
            mock_session_local.return_value = session

            from main import app

            result = runner.invoke(app, ["seed"])
            assert result.exit_code == 0
            assert "✅" in result.stdout or "ℹ️" in result.stdout


class TestQuizCommand:
    @pytest.mark.parametrize("rounds", [1, 3, 5])
    def test_quiz_with_rounds(self, rounds):
        with (
            patch("main._init_db"),
            patch("main.SessionLocal") as mock_session_local,
        ):
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker

            engine = create_engine(
                "sqlite:///:memory:",
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )
            Base.metadata.create_all(bind=engine)
            session_factory = sessionmaker(bind=engine)
            session = session_factory()
            _init_test_db(session)
            mock_session_local.return_value = session

            from main import app

            result = runner.invoke(
                app, ["quiz", "--rounds", str(rounds)], input="read read\n" * rounds
            )
            assert result.exit_code == 0
            assert "Result:" in result.stdout

    def test_quiz_empty_db_shows_warning(self):
        with (
            patch("main._init_db"),
            patch("main.SessionLocal") as mock_session_local,
        ):
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker

            engine = create_engine(
                "sqlite:///:memory:",
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )
            Base.metadata.create_all(bind=engine)
            session_factory = sessionmaker(bind=engine)
            session = session_factory()
            mock_session_local.return_value = session

            from main import app

            result = runner.invoke(app, ["quiz"])
            assert result.exit_code == 1
            assert "No verbs found" in result.stdout

    def test_quiz_specific_verb(self):
        with (
            patch("main._init_db"),
            patch("main.SessionLocal") as mock_session_local,
        ):
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker

            engine = create_engine(
                "sqlite:///:memory:",
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )
            Base.metadata.create_all(bind=engine)
            session_factory = sessionmaker(bind=engine)
            session = session_factory()
            _init_test_db(session)
            mock_session_local.return_value = session

            from main import app

            result = runner.invoke(
                app, ["quiz", "--verb", "read", "--rounds", "1"], input="read read\n"
            )
            assert result.exit_code == 0
            assert "READ" in result.stdout

    def test_quiz_unknown_verb(self):
        with (
            patch("main._init_db"),
            patch("main.SessionLocal") as mock_session_local,
        ):
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker

            engine = create_engine(
                "sqlite:///:memory:",
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )
            Base.metadata.create_all(bind=engine)
            session_factory = sessionmaker(bind=engine)
            session = session_factory()
            _init_test_db(session)
            mock_session_local.return_value = session

            from main import app

            result = runner.invoke(
                app, ["quiz", "--verb", "xyzunknown"], input="read read\n"
            )
            assert result.exit_code == 1
            assert "not found" in result.stdout


class TestStatsCommand:
    def test_stats_empty(self):
        with (
            patch("main._init_db"),
            patch("main.SessionLocal") as mock_session_local,
        ):
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker

            engine = create_engine(
                "sqlite:///:memory:",
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )
            Base.metadata.create_all(bind=engine)
            session_factory = sessionmaker(bind=engine)
            session = session_factory()
            mock_session_local.return_value = session

            from main import app

            result = runner.invoke(app, ["stats"])
            assert result.exit_code == 0
            assert "0" in result.stdout

    def test_stats_with_data(self):
        with (
            patch("main._init_db"),
            patch("main.SessionLocal") as mock_session_local,
        ):
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker

            from app.models import UserAttempt

            engine = create_engine(
                "sqlite:///:memory:",
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )
            Base.metadata.create_all(bind=engine)
            session_factory = sessionmaker(bind=engine)
            session = session_factory()
            _init_test_db(session)

            verb = session.query(Verb).first()
            assert verb is not None
            session.add(
                UserAttempt(
                    verb_id=verb.id,
                    past_given="read",
                    participle_given="read",
                    is_correct=True,
                )
            )
            session.add(
                UserAttempt(
                    verb_id=verb.id,
                    past_given="wrong",
                    participle_given="wrong",
                    is_correct=False,
                )
            )
            session.commit()
            mock_session_local.return_value = session

            from main import app

            result = runner.invoke(app, ["stats"])
            assert result.exit_code == 0
            assert "50.0" in result.stdout or "50" in result.stdout
