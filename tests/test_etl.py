"""
Integration-style tests for the ETL pipeline (mocked DB).
"""

from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

import pandas as pd
import pytest

from src.etl import run_pipeline


SAMPLE_API_RESPONSE = {
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


@patch("src.etl.get_cursor")
@patch("src.etl.upsert_location", return_value=1)
@patch("src.etl.fetch_weather", return_value=SAMPLE_API_RESPONSE)
def test_run_pipeline_success(mock_fetch, mock_upsert_loc, mock_cursor):
    """Pipeline runs end-to-end and calls all expected DB operations."""
    # Mock cursor context manager
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = (1,)
    mock_cursor.return_value.__enter__ = MagicMock(return_value=mock_cur)
    mock_cursor.return_value.__exit__ = MagicMock(return_value=False)

    run_pipeline()

    mock_fetch.assert_called_once()
    mock_upsert_loc.assert_called_once()
    # executemany called for hourly + daily inserts
    assert mock_cur.executemany.call_count == 2


@patch("src.etl.get_cursor")
@patch("src.etl.fetch_weather", side_effect=ConnectionError("Network down"))
def test_run_pipeline_failure(mock_fetch, mock_cursor):
    """Pipeline logs failure and re-raises on API error."""
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = (1,)
    mock_cursor.return_value.__enter__ = MagicMock(return_value=mock_cur)
    mock_cursor.return_value.__exit__ = MagicMock(return_value=False)

    with pytest.raises(ConnectionError):
        run_pipeline()
