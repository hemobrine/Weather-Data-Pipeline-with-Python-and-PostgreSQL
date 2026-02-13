"""
Open-Meteo API client — fetches weather forecast data.
"""

import requests
from src.logger import logger


BASE_URL = "https://api.open-meteo.com/v1/forecast"


def fetch_weather(
    latitude: float,
    longitude: float,
    hourly_vars: str,
    daily_vars: str,
    forecast_days: int = 7,
    timezone: str = "auto",
) -> dict:
    """
    Fetch weather data from the Open-Meteo API.

    Args:
        latitude:      Location latitude.
        longitude:     Location longitude.
        hourly_vars:   Comma-separated hourly variable names.
        daily_vars:    Comma-separated daily variable names.
        forecast_days: Number of forecast days (1–16).
        timezone:      Timezone string or "auto".

    Returns:
        Raw JSON response as a Python dict.

    Raises:
        requests.HTTPError:  On non-2xx status codes.
        ValueError:          If the API returns an error payload.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": hourly_vars,
        "daily": daily_vars,
        "forecast_days": forecast_days,
        "timezone": timezone,
    }

    logger.info(
        "Fetching weather data for (%.4f, %.4f) — %d day(s)",
        latitude,
        longitude,
        forecast_days,
    )

    response = requests.get(BASE_URL, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()

    # Open-Meteo returns {"error": true, "reason": "..."} on bad params
    if data.get("error"):
        raise ValueError(f"Open-Meteo API error: {data.get('reason', 'unknown')}")

    logger.info(
        "Received data — hourly points: %d, daily points: %d",
        len(data.get("hourly", {}).get("time", [])),
        len(data.get("daily", {}).get("time", [])),
    )

    return data
