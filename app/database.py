"""SQLAlchemy engine and session factory.

Reads DATABASE_URL from the .env file (or environment variables).
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set. "
        "Create a .env file with DATABASE_URL=postgresql://user:pass@host:5432/dbname"
    )

_is_sqlite = DATABASE_URL.startswith("sqlite") if DATABASE_URL else False

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"connect_timeout": 10} if not _is_sqlite else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Yield a database session and ensure it is closed afterward."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_migrations():
    """Create tables and run safe schema migrations."""
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        exists = conn.execute(
            text(
                "SELECT 1 FROM information_schema.columns "
                "WHERE table_name='verbs' AND column_name='meaning'"
            )
        ).fetchone()
        if not exists:
            conn.execute(text("ALTER TABLE verbs ADD COLUMN meaning VARCHAR(150)"))
            conn.commit()
