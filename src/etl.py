"""
ETL orchestrator — Extract, Transform, Load pipeline for weather data.
"""

from datetime import datetime, timezone

import pandas as pd

from config.settings import settings
from src.api_client import fetch_weather
from src.data_cleaning import normalize_hourly, normalize_daily, add_metadata
from src.db import get_cursor, upsert_location
from src.logger import logger


def _log_pipeline_start() -> int:
    """Insert a new pipeline_runs row and return its id."""
    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO pipeline_runs (started_at, status)
            VALUES (%s, 'running')
            RETURNING id
            """,
            (datetime.now(timezone.utc),),
        )
        run_id = cur.fetchone()[0]
    logger.info("Pipeline run #%d started", run_id)
    return run_id


def _log_pipeline_end(run_id: int, status: str,
                      rows_hourly: int = 0, rows_daily: int = 0,
                      error_msg: str = None):
    """Update the pipeline_runs row with results."""
    with get_cursor() as cur:
        cur.execute(
            """
            UPDATE pipeline_runs
            SET finished_at = %s,
                status      = %s,
                rows_hourly = %s,
                rows_daily  = %s,
                error_msg   = %s
            WHERE id = %s
            """,
            (datetime.now(timezone.utc), status, rows_hourly, rows_daily, error_msg, run_id),
        )


def _upsert_hourly(cur, location_id: int, df: pd.DataFrame) -> int:
    """Batch-upsert hourly weather rows. Returns count of rows upserted."""
    if df.empty:
        return 0

    rows = [
        (
            location_id,
            row["timestamp"],
            row.get("temperature_2m"),
            row.get("humidity_2m"),
            row.get("wind_speed_10m"),
            row.get("precipitation"),
            row.get("fetched_at"),
        )
        for _, row in df.iterrows()
    ]

    cur.executemany(
        """
        INSERT INTO hourly_weather
            (location_id, timestamp, temperature_2m, humidity_2m,
             wind_speed_10m, precipitation, fetched_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (location_id, timestamp)
        DO UPDATE SET
            temperature_2m  = EXCLUDED.temperature_2m,
            humidity_2m     = EXCLUDED.humidity_2m,
            wind_speed_10m  = EXCLUDED.wind_speed_10m,
            precipitation   = EXCLUDED.precipitation,
            fetched_at      = EXCLUDED.fetched_at
        """,
        rows,
    )
    return len(rows)


def _upsert_daily(cur, location_id: int, df: pd.DataFrame) -> int:
    """Batch-upsert daily weather rows. Returns count of rows upserted."""
    if df.empty:
        return 0

    rows = [
        (
            location_id,
            row["date"],
            row.get("temp_max"),
            row.get("temp_min"),
            row.get("precipitation_sum"),
            row.get("fetched_at"),
        )
        for _, row in df.iterrows()
    ]

    cur.executemany(
        """
        INSERT INTO daily_weather
            (location_id, date, temp_max, temp_min,
             precipitation_sum, fetched_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (location_id, date)
        DO UPDATE SET
            temp_max          = EXCLUDED.temp_max,
            temp_min          = EXCLUDED.temp_min,
            precipitation_sum = EXCLUDED.precipitation_sum,
            fetched_at        = EXCLUDED.fetched_at
        """,
        rows,
    )
    return len(rows)


def run_pipeline():
    """
    Full ETL pipeline:
    1. Log start
    2. Fetch raw weather JSON
    3. Normalize + clean hourly & daily DataFrames
    4. Upsert location
    5. Upsert hourly & daily weather rows
    6. Log completion
    """
    run_id = _log_pipeline_start()

    try:
        # ── Extract ──────────────────────────────────────────
        raw = fetch_weather(
            latitude=settings.API_LATITUDE,
            longitude=settings.API_LONGITUDE,
            hourly_vars=settings.API_HOURLY_VARS,
            daily_vars=settings.API_DAILY_VARS,
        )

        # ── Transform ───────────────────────────────────────
        df_hourly = normalize_hourly(raw)
        df_daily = normalize_daily(raw)

        df_hourly = add_metadata(df_hourly, settings.API_LATITUDE, settings.API_LONGITUDE)
        df_daily = add_metadata(df_daily, settings.API_LATITUDE, settings.API_LONGITUDE)

        # ── Load ─────────────────────────────────────────────
        location_id = upsert_location(
            latitude=raw.get("latitude", settings.API_LATITUDE),
            longitude=raw.get("longitude", settings.API_LONGITUDE),
            elevation=raw.get("elevation"),
            tz=raw.get("timezone"),
        )

        with get_cursor() as cur:
            hourly_count = _upsert_hourly(cur, location_id, df_hourly)
            daily_count = _upsert_daily(cur, location_id, df_daily)

        # ── Log success ──────────────────────────────────────
        _log_pipeline_end(run_id, "completed", hourly_count, daily_count)
        logger.info(
            "Pipeline run #%d completed — %d hourly, %d daily rows upserted",
            run_id, hourly_count, daily_count,
        )

    except Exception as exc:
        logger.error("Pipeline run #%d failed: %s", run_id, exc, exc_info=True)
        _log_pipeline_end(run_id, "failed", error_msg=str(exc))
        raise
