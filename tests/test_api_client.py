"""
Unit tests for the Open-Meteo API client.
"""

import pytest
from unittest.mock import patch, MagicMock

from src.api_client import fetch_weather


SAMPLE_RESPONSE = {
    "latitude": 30.05,
    "longitude": 31.25,
    "elevation": 75.0,
    "timezone": "Africa/Cairo",
    "hourly": {
        "time": ["2026-02-13T00:00", "2026-02-13T01:00"],
        "temperature_2m": [15.2, 14.8],
        "relative_humidity_2m": [62, 65],
        "wind_speed_10m": [8.5, 7.2],
        "precipitation": [0.0, 0.0],
    },
    "daily": {
        "time": ["2026-02-13"],
        "temperature_2m_max": [22.1],
        "temperature_2m_min": [12.3],
        "precipitation_sum": [0.0],
    },
}


@patch("src.api_client.requests.get")
def test_fetch_weather_success(mock_get):
    """Successful API call returns parsed JSON."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = SAMPLE_RESPONSE
    mock_resp.raise_for_status.return_value = None
    mock_get.return_value = mock_resp

    result = fetch_weather(30.0444, 31.2357, "temperature_2m", "temperature_2m_max")

    assert result["latitude"] == 30.05
    assert len(result["hourly"]["time"]) == 2
    assert len(result["daily"]["time"]) == 1
    mock_get.assert_called_once()


@patch("src.api_client.requests.get")
def test_fetch_weather_api_error(mock_get):
    """API error payload raises ValueError."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"error": True, "reason": "Bad parameter"}
    mock_resp.raise_for_status.return_value = None
    mock_get.return_value = mock_resp

    with pytest.raises(ValueError, match="Bad parameter"):
        fetch_weather(30.0444, 31.2357, "bad_param", "temperature_2m_max")


@patch("src.api_client.requests.get")
def test_fetch_weather_http_error(mock_get):
    """Non-2xx status raises HTTPError."""
    import requests

    mock_resp = MagicMock()
    mock_resp.raise_for_status.side_effect = requests.HTTPError("500 Server Error")
    mock_get.return_value = mock_resp

    with pytest.raises(requests.HTTPError):
        fetch_weather(30.0444, 31.2357, "temperature_2m", "temperature_2m_max")
