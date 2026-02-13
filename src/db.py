"""
PostgreSQL connection helper and schema initializer.
"""

import os
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import execute_values

from config.settings import settings
from src.logger import logger


def get_connection():
    """
    Create and return a new PostgreSQL connection using app settings.
    """
    conn = psycopg2.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        dbname=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
    )
    return conn


@contextmanager
def get_cursor(commit: bool = True):
    """
    Context manager that yields a cursor and handles commit/rollback.

    Usage::

        with get_cursor() as cur:
            cur.execute("SELECT 1")
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        yield cur
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def init_schema():
    """
    Execute ``sql/schema.sql`` to create tables if they don't exist.
    """
    schema_path = os.path.join(os.path.dirname(__file__), "..", "sql", "schema.sql")
    schema_path = os.path.abspath(schema_path)

    logger.info("Initializing database schema from %s", schema_path)

    with open(schema_path, "r", encoding="utf-8") as f:
        sql = f.read()

    with get_cursor() as cur:
        cur.execute(sql)

    logger.info("Database schema initialized successfully")


def upsert_location(latitude: float, longitude: float,
                    elevation: float = None, tz: str = None) -> int:
    """
    Insert or fetch the location row. Returns the ``location_id``.
    """
    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO locations (latitude, longitude, elevation, timezone)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (latitude, longitude)
            DO UPDATE SET elevation = EXCLUDED.elevation,
                          timezone  = EXCLUDED.timezone
            RETURNING id
            """,
            (latitude, longitude, elevation, tz),
        )
        location_id = cur.fetchone()[0]

    logger.info("Location id=%d for (%.4f, %.4f)", location_id, latitude, longitude)
    return location_id
