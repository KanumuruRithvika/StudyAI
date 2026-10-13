import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.database_models import Base


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./learning.db")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

engine_kwargs = {}

if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {
        "check_same_thread": False,
    }

engine = create_engine(
    DATABASE_URL,
    **engine_kwargs,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def init_database() -> None:
    """Create database tables and apply project migrations."""
    Base.metadata.create_all(
        bind=engine
    )

    from database.migration import migrate_database

    migrate_database()


def get_db():
    """Provide a database session for FastAPI dependencies."""
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()