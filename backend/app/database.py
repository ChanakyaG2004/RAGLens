"""SQLAlchemy setup and small development-schema migrations."""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import get_settings

settings = get_settings()
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""


def get_db():
    """Provide a transaction-scoped database session to FastAPI endpoints."""
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()


def initialize_database() -> None:
    """Create the pgvector extension, tables, and additive development columns."""
    from . import models  # noqa: F401 - imports mapped models before create_all

    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

    Base.metadata.create_all(bind=engine)

    # This project intentionally avoids an Alembic dependency for its MVP. These
    # additive migrations let existing local demo databases gain trace timings.
    timing_columns = ("embedding_ms", "retrieval_ms", "generation_ms", "total_ms")
    score_columns = ("faithfulness", "context_relevance", "citation_support", "hallucination_risk")
    with engine.begin() as connection:
        for column in timing_columns:
            connection.execute(
                text(f"ALTER TABLE traces ADD COLUMN IF NOT EXISTS {column} INTEGER NOT NULL DEFAULT 0")
            )
        for column in score_columns:
            connection.execute(text(f"ALTER TABLE traces ADD COLUMN IF NOT EXISTS {column} DOUBLE PRECISION"))
