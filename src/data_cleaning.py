"""
Data cleaning & normalization — converts raw Open-Meteo JSON into
clean pandas DataFrames ready for database insertion.
"""

from datetime import datetime, timezone

import pandas as pd

from src.logger import logger


def normalize_hourly(raw: dict) -> pd.DataFrame:
    """
    Flatten the ``hourly`` block of an Open-Meteo response into a DataFrame.

    Columns produced:
        timestamp, temperature_2m, relative_humidity_2m,
        wind_speed_10m, precipitation
    """
    hourly = raw.get("hourly")
    if not hourly or "time" not in hourly:
        logger.warning("No hourly data found in API response")
        return pd.DataFrame()

    df = pd.DataFrame(hourly)
    df.rename(columns={"time": "timestamp"}, inplace=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    # Rename to match DB columns
    rename_map = {
        "relative_humidity_2m": "humidity_2m",
    }
    df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

    # Drop rows where ALL weather values are null
    weather_cols = [c for c in df.columns if c != "timestamp"]
    df.dropna(subset=weather_cols, how="all", inplace=True)

    logger.info("Normalized %d hourly records", len(df))
    return df


def normalize_daily(raw: dict) -> pd.DataFrame:
    """
    Flatten the ``daily`` block of an Open-Meteo response into a DataFrame.

    Columns produced:
        date, temperature_2m_max, temperature_2m_min, precipitation_sum
    """
    daily = raw.get("daily")
    if not daily or "time" not in daily:
        logger.warning("No daily data found in API response")
        return pd.DataFrame()

    df = pd.DataFrame(daily)
    df.rename(columns={"time": "date"}, inplace=True)
    df["date"] = pd.to_datetime(df["date"]).dt.date

    # Rename to match DB columns
    rename_map = {
        "temperature_2m_max": "temp_max",
        "temperature_2m_min": "temp_min",
    }
    df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

    # Drop rows where ALL weather values are null
    weather_cols = [c for c in df.columns if c != "date"]
    df.dropna(subset=weather_cols, how="all", inplace=True)

    logger.info("Normalized %d daily records", len(df))
    return df


def add_metadata(df: pd.DataFrame, latitude: float, longitude: float) -> pd.DataFrame:
    """
    Append ``latitude``, ``longitude``, and ``fetched_at`` columns to a DataFrame.
    """
    if df.empty:
        return df

    df = df.copy()
    df["latitude"] = latitude
    df["longitude"] = longitude
    df["fetched_at"] = datetime.now(timezone.utc)
    return df
