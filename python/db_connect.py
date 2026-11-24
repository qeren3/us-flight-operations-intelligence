"""Shared PostgreSQL configuration and SQLAlchemy connection helpers."""

from __future__ import annotations

import os
from functools import lru_cache

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine
from sqlalchemy.engine import URL
from sqlalchemy.exc import SQLAlchemyError

# Local development convenience; existing process environment values take precedence.
load_dotenv()

_REQUIRED_SETTINGS = ("DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD")


class DatabaseConfigurationError(ValueError):
    """Raised when required database settings are missing or invalid."""


def _database_url() -> URL:
    missing = [name for name in _REQUIRED_SETTINGS if not os.getenv(name)]
    if missing:
        raise DatabaseConfigurationError(
            "Missing required database configuration: " + ", ".join(missing)
            + ". Set these environment variables or add them to .env."
        )

    try:
        port = int(os.environ["DB_PORT"])
        if not 1 <= port <= 65535:
            raise ValueError
    except ValueError:
        raise DatabaseConfigurationError("DB_PORT must be an integer from 1 to 65535.") from None

    return URL.create(
        drivername="postgresql+psycopg2",
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=port,
        database=os.environ["DB_NAME"],
    )


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Return a lazily connected, reusable SQLAlchemy engine."""
    return create_engine(_database_url(), pool_pre_ping=True, pool_recycle=1800)


def read_query(query: str) -> pd.DataFrame:
    """Run a query and expose a sanitized error if the database is unavailable."""
    try:
        return pd.read_sql_query(query, get_engine())
    except SQLAlchemyError:
        raise RuntimeError(
            "Could not query PostgreSQL. Check that the database is reachable and "
            "the configured connection settings are correct."
        ) from None
