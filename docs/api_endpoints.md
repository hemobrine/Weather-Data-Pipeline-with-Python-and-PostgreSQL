# API Endpoints

## Open-Meteo Forecast API

The pipeline uses the **Open-Meteo Weather Forecast API** — a free, open-source weather API that requires no API key.

### Base URL

```
https://api.open-meteo.com/v1/forecast
```

### Request Parameters

| Parameter       | Type   | Example                                 | Description                      |
| --------------- | ------ | --------------------------------------- | -------------------------------- |
| `latitude`      | float  | `30.0444`                               | Location latitude                |
| `longitude`     | float  | `31.2357`                               | Location longitude               |
| `hourly`        | string | `temperature_2m,precipitation`          | Comma-separated hourly variables |
| `daily`         | string | `temperature_2m_max,temperature_2m_min` | Comma-separated daily variables  |
| `forecast_days` | int    | `7`                                     | Days of forecast (1–16)          |
| `timezone`      | string | `auto`                                  | Timezone for timestamps          |

### Hourly Variables Used

| Variable               | Unit | Description                  |
| ---------------------- | ---- | ---------------------------- |
| `temperature_2m`       | °C   | Air temperature at 2m height |
| `relative_humidity_2m` | %    | Relative humidity at 2m      |
| `wind_speed_10m`       | km/h | Wind speed at 10m height     |
| `precipitation`        | mm   | Precipitation (rain + snow)  |

### Daily Variables Used

| Variable             | Unit | Description               |
| -------------------- | ---- | ------------------------- |
| `temperature_2m_max` | °C   | Maximum daily temperature |
| `temperature_2m_min` | °C   | Minimum daily temperature |
| `precipitation_sum`  | mm   | Total daily precipitation |

### Example Request

```
GET https://api.open-meteo.com/v1/forecast?latitude=30.0444&longitude=31.2357&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto
```

### Example Response (truncated)

```json
{
  "latitude": 30.05,
  "longitude": 31.25,
  "elevation": 75.0,
  "timezone": "Africa/Cairo",
  "hourly": {
    "time": ["2026-02-13T00:00", "2026-02-13T01:00", "..."],
    "temperature_2m": [15.2, 14.8, "..."],
    "relative_humidity_2m": [62, 65, "..."],
    "wind_speed_10m": [8.5, 7.2, "..."],
    "precipitation": [0.0, 0.0, "..."]
  },
  "daily": {
    "time": ["2026-02-13"],
    "temperature_2m_max": [22.1],
    "temperature_2m_min": [12.3],
    "precipitation_sum": [0.0]
  }
}
```

### Error Response

```json
{
  "error": true,
  "reason": "Cannot initialize WeatherVariable from invalid String value"
}
```

### Rate Limits

- **Non-commercial use**: Free, no API key required
- **10,000 requests/day** for non-commercial use
- For higher volumes, see [open-meteo.com/en/pricing](https://open-meteo.com/en/pricing)
