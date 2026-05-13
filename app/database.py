"""SQLAlchemy engine and session factory.

Reads DATABASE_URL from the .env file (or environment variables).
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set. "
        "Create a .env file with DATABASE_URL=postgresql://user:pass@host:5432/dbname"
    )

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"connect_timeout": 10},  # fail fast instead of hanging
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
