import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, date

from src.db import get_connection

st.set_page_config(layout="wide", page_title="Weather Dashboard 🌦️")

@st.cache_data(ttl=60)
def load_data():
    conn = get_connection()
    try:
        query_hourly = """
            SELECT timestamp, temperature_2m, humidity_2m, wind_speed_10m, precipitation
            FROM hourly_weather
            ORDER BY timestamp DESC;
        """
        query_daily = """
            SELECT date, temp_max, temp_min, precipitation_sum
            FROM daily_weather
            ORDER BY date DESC;
        """
        query_runs = """
            SELECT id, started_at, finished_at, status, rows_hourly, rows_daily
            FROM pipeline_runs
            ORDER BY started_at DESC
            LIMIT 10;
        """
        
        df_hourly = pd.read_sql(query_hourly, conn)
        df_daily = pd.read_sql(query_daily, conn)
        df_runs = pd.read_sql(query_runs, conn)
        
        return df_hourly, df_daily, df_runs
    finally:
        conn.close()

st.title("🌦️ Weather Data Pipeline Dashboard")

try:
    df_hourly, df_daily, df_runs = load_data()

    # --- Refresh Button ---
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    
    with col5:
        if st.button("🔄 Refresh Data", type="primary"):
            with st.spinner("Fetching latest weather data..."):
                try:
                    from src.etl import run_pipeline
                    run_pipeline()
                    st.success("Data updated successfully!")
                    st.cache_data.clear() # Clear cache to show new data
                    st.rerun()
                except Exception as e:
                    st.error(f"Update failed: {e}")

    # --- Metrics Row ---
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    
    latest_hourly = df_hourly.iloc[0] if not df_hourly.empty else None
    latest_run = df_runs.iloc[0] if not df_runs.empty else None

    if latest_hourly is not None:
        m_col1.metric("Current Temp", f"{latest_hourly['temperature_2m']} °C")
        m_col2.metric("Humidity", f"{latest_hourly['humidity_2m']} %")
        m_col3.metric("Wind Speed", f"{latest_hourly['wind_speed_10m']} km/h")
    
    if latest_run is not None:
        status_color = "🟢" if latest_run['status'] == 'completed' else "🔴"
        m_col4.metric("Last Pipeline Run", f"{status_color} {latest_run['status'].title()}")

    st.markdown("---")

    # --- Charts Row ---
    st.subheader("Temperature & Humidity Trends (Hourly)")
    
    chart_data = df_hourly.head(168).sort_values("timestamp") # Last 7 days
    
    base = alt.Chart(chart_data).encode(x='timestamp:T')

    line_temp = base.mark_line(color='orange').encode(
        y=alt.Y('temperature_2m', title='Temperature (°C)'),
        tooltip=['timestamp', 'temperature_2m']
    )
    
    line_humidity = base.mark_line(color='blue').encode(
        y=alt.Y('humidity_2m', title='Humidity (%)'),
        tooltip=['timestamp', 'humidity_2m']
    )

    st.altair_chart((line_temp + line_humidity).interactive(), use_container_width=True)

    col_daily_chart, col_runs_table = st.columns([2, 1])

    with col_daily_chart:
        st.subheader("Daily Precipitation (Last 7 Days)")
        daily_chart_data = df_daily.head(7).sort_values("date")
        
        bar_chart = alt.Chart(daily_chart_data).mark_bar().encode(
            x='date:T',
            y='precipitation_sum:Q',
            tooltip=['date', 'precipitation_sum']
        ).interactive()
        
        st.altair_chart(bar_chart, use_container_width=True)

    with col_runs_table:
        st.subheader("Recent Pipeline Runs")
        st.dataframe(df_runs[['started_at', 'status', 'rows_hourly']], hide_index=True)

except Exception as e:
    st.error(f"Error loading dashboard: {e}")
    st.info("Make sure the database is running and the pipeline has executed at least once.")
