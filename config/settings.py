"""
Application settings loaded from environment variables / .env file.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Pipeline configuration — all values can be overridden via env vars."""

    # ── Database ──────────────────────────────────────────────
    DB_HOST: str = Field(default="localhost", description="PostgreSQL host")
    DB_PORT: int = Field(default=5432, description="PostgreSQL port")
    DB_NAME: str = Field(default="weather_db", description="Database name")
    DB_USER: str = Field(default="weather_user", description="Database user")
    DB_PASSWORD: str = Field(default="weather_pass", description="Database password")

    # ── Open-Meteo API ────────────────────────────────────────
    API_LATITUDE: float = Field(default=30.0444, description="Latitude (default: Cairo)")
    API_LONGITUDE: float = Field(default=31.2357, description="Longitude (default: Cairo)")
    API_HOURLY_VARS: str = Field(
        default="temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation",
        description="Comma-separated hourly weather variables",
    )
    API_DAILY_VARS: str = Field(
        default="temperature_2m_max,temperature_2m_min,precipitation_sum",
        description="Comma-separated daily weather variables",
    )

    # ── Scheduler ─────────────────────────────────────────────
    SCHEDULE_HOUR: int = Field(default=6, description="Hour of day (0-23) for daily run")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


# Singleton instance
settings = Settings()
