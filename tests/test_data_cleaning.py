"""
Unit tests for data normalization and cleaning.
"""

import pandas as pd

from src.data_cleaning import normalize_hourly, normalize_daily, add_metadata


SAMPLE_RAW = {
    "hourly": {
        "time": [
            "2026-02-13T00:00",
            "2026-02-13T01:00",
            "2026-02-13T02:00",
        ],
        "temperature_2m": [15.2, 14.8, None],
        "relative_humidity_2m": [62, 65, None],
        "wind_speed_10m": [8.5, 7.2, None],
        "precipitation": [0.0, 0.0, None],
    },
    "daily": {
        "time": ["2026-02-13", "2026-02-14"],
        "temperature_2m_max": [22.1, 23.0],
        "temperature_2m_min": [12.3, 11.5],
        "precipitation_sum": [0.0, 1.2],
    },
}


class TestNormalizeHourly:
    def test_basic_normalization(self):
        df = normalize_hourly(SAMPLE_RAW)
        assert "timestamp" in df.columns
        assert "humidity_2m" in df.columns  # renamed from relative_humidity_2m
        assert len(df) == 2  # row with all-None weather values is dropped

    def test_empty_response(self):
        df = normalize_hourly({})
        assert df.empty

    def test_no_time_key(self):
        df = normalize_hourly({"hourly": {"temperature_2m": [1, 2]}})
        assert df.empty


class TestNormalizeDaily:
    def test_basic_normalization(self):
        df = normalize_daily(SAMPLE_RAW)
        assert "date" in df.columns
        assert "temp_max" in df.columns  # renamed
        assert "temp_min" in df.columns  # renamed
        assert len(df) == 2

    def test_empty_response(self):
        df = normalize_daily({})
        assert df.empty


class TestAddMetadata:
    def test_adds_columns(self):
        df = pd.DataFrame({"value": [1, 2, 3]})
        result = add_metadata(df, 30.0, 31.0)
        assert "latitude" in result.columns
        assert "longitude" in result.columns
        assert "fetched_at" in result.columns
        assert result["latitude"].iloc[0] == 30.0

    def test_empty_df(self):
        df = pd.DataFrame()
        result = add_metadata(df, 30.0, 31.0)
        assert result.empty
