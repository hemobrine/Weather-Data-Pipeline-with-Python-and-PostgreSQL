-- ============================================================
-- Weather Data Pipeline — PostgreSQL Schema
-- ============================================================

-- Locations table (one row per unique lat/lon)
CREATE TABLE IF NOT EXISTS locations (
    id          SERIAL PRIMARY KEY,
    latitude    DECIMAL(8, 5) NOT NULL,
    longitude   DECIMAL(8, 5) NOT NULL,
    elevation   DECIMAL(7, 2),
    timezone    VARCHAR(50),
    UNIQUE (latitude, longitude)
);

-- Hourly weather observations
CREATE TABLE IF NOT EXISTS hourly_weather (
    id              SERIAL PRIMARY KEY,
    location_id     INT NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
    timestamp       TIMESTAMPTZ NOT NULL,
    temperature_2m  DECIMAL(5, 2),
    humidity_2m     DECIMAL(5, 2),
    wind_speed_10m  DECIMAL(6, 2),
    precipitation   DECIMAL(6, 2),
    fetched_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (location_id, timestamp)
);

-- Daily weather summaries
CREATE TABLE IF NOT EXISTS daily_weather (
    id                  SERIAL PRIMARY KEY,
    location_id         INT NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
    date                DATE NOT NULL,
    temp_max            DECIMAL(5, 2),
    temp_min            DECIMAL(5, 2),
    precipitation_sum   DECIMAL(6, 2),
    fetched_at          TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (location_id, date)
);

-- Pipeline run tracking
CREATE TABLE IF NOT EXISTS pipeline_runs (
    id          SERIAL PRIMARY KEY,
    started_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,
    status      VARCHAR(20) DEFAULT 'running',
    error_msg   TEXT,
    rows_hourly INT DEFAULT 0,
    rows_daily  INT DEFAULT 0
);

-- ── Indexes for common queries ──────────────────────────────
CREATE INDEX IF NOT EXISTS idx_hourly_location_ts
    ON hourly_weather (location_id, timestamp);

CREATE INDEX IF NOT EXISTS idx_daily_location_date
    ON daily_weather (location_id, date);

CREATE INDEX IF NOT EXISTS idx_pipeline_runs_status
    ON pipeline_runs (status);
