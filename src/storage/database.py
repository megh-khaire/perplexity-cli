"""Database configuration and session management."""

import os
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker


def get_database_url() -> str:
    """Get the database URL from environment or default location."""
    db_path = os.getenv("PERPLEXITY_CLI_DB_PATH")
    if not db_path:
        # Default to ~/.perplexity-cli/conversations.db
        home_dir = Path.home()
        config_dir = home_dir / ".perplexity-cli"
        config_dir.mkdir(exist_ok=True)
        db_path = config_dir / "conversations.db"

    return f"sqlite:///{db_path}"


engine = create_engine(
    get_database_url(),
    echo=False,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_database():
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_database_session() -> Session:
    """Get a database session with proper cleanup."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_session() -> Session:
    """Get a database session for dependency injection."""
    return SessionLocal()
