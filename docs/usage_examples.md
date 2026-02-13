# Usage Examples

## Starting the Pipeline

### With Docker (recommended)

```bash
# Start all services
docker compose up --build -d

# View live logs
docker compose logs -f pipeline

# Stop all services
docker compose down
```

### Without Docker (local development)

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables (or create .env from .env.example)
cp .env.example .env
# Edit .env — set DB_HOST=localhost and your PostgreSQL credentials

# Run the pipeline
python main.py
```

---

## Querying the Database

Connect to the database:

```bash
# Via Docker
docker compose exec db psql -U weather_user -d weather_db

# Direct connection
psql -h localhost -U weather_user -d weather_db
```

### Example Queries

**1. Latest hourly temperatures:**

```sql
SELECT timestamp, temperature_2m, humidity_2m, wind_speed_10m
FROM hourly_weather
ORDER BY timestamp DESC
LIMIT 24;
```

**2. Average temperature this week:**

```sql
SELECT
    date,
    temp_max,
    temp_min,
    ROUND((temp_max + temp_min) / 2, 1) AS temp_avg
FROM daily_weather
ORDER BY date DESC
LIMIT 7;
```

**3. Total precipitation over the last 7 days:**

```sql
SELECT SUM(precipitation_sum) AS total_precip_mm
FROM daily_weather
WHERE date >= CURRENT_DATE - INTERVAL '7 days';
```

**4. Hourly wind speed trends for today:**

```sql
SELECT
    timestamp,
    wind_speed_10m
FROM hourly_weather
WHERE timestamp::date = CURRENT_DATE
ORDER BY timestamp;
```

**5. Pipeline run history:**

```sql
SELECT
    id,
    started_at,
    finished_at,
    status,
    rows_hourly,
    rows_daily,
    error_msg
FROM pipeline_runs
ORDER BY started_at DESC
LIMIT 10;
```

---

## Multi-City Setup

To track multiple cities, run the pipeline with different coordinates. Update your `.env` or pass environment variables:

```bash
# Cairo (default)
docker compose up -d

# Add another city by running a second pipeline instance
docker compose run -e API_LATITUDE=51.5074 -e API_LONGITUDE=-0.1278 pipeline
```

Each city gets its own row in `locations` and its weather data is stored separately.

---

## Extending Weather Variables

To add more variables (e.g., UV index, cloud cover):

1. **Update `.env`:**

   ```
   API_HOURLY_VARS=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation,uv_index,cloud_cover
   ```

2. **Add columns to `sql/schema.sql`:**

   ```sql
   ALTER TABLE hourly_weather ADD COLUMN uv_index DECIMAL(4,2);
   ALTER TABLE hourly_weather ADD COLUMN cloud_cover DECIMAL(5,2);
   ```

3. **Update `data_cleaning.py`** to handle the new columns.

4. **Update `etl.py`** upsert queries to include new fields.

See [Open-Meteo docs](https://open-meteo.com/en/docs) for all available variables.
