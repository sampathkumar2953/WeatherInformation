import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Get DB connection URL from environment, default to local SQLite file
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./weather.db")

# Special connection args for SQLite to allow usage across threads (needed for FastAPI)
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# Create SQLAlchemy engine (shared by app and scripts)
engine = create_engine(DATABASE_URL, echo=False, future=True, connect_args=connect_args)

# Session factory for DB operations (one session per request/task)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

# Base class for ORM models to inherit from
Base = declarative_base()
