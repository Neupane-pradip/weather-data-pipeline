import os
from pathlib import Path

import pandas as pd
import psycopg
import streamlit as st
from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parent / ".env")

st.set_page_config(
    page_title="Weather Pipeline Dashboard",
    layout="wide",
)

def load_weather():
    query = """
        SELECT
            city,
            weather_time_utc,
            temperature_c,
            collected_at
        FROM weather_observations
        WHERE source = 'open-meteo'
        ORDER BY weather_time_utc ASC, city ASC;
    """

    with psycopg.connect(
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        connect_timeout=10,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()

    data = pd.DataFrame(
        rows,
        columns=[
            "city",
            "weather_time_utc",
            "temperature_c",
            "collected_at",
        ],
    )

    data["weather_time_utc"] = pd.to_datetime(
        data["weather_time_utc"], utc=True
    )
    data["collected_at"] = pd.to_datetime(
        data["collected_at"], utc=True
    )

    return data

st.title("Weather Pipeline Dashboard")
st.caption("Saved weather for Helsinki, London, and Berlin. Times are UTC.")

st.button("Refresh saved data")

try:
    data = load_weather()
except (psycopg.Error, KeyError):
    st.error(
        "Could not load weather. Check PostgreSQL and your .env settings."
    )
    st.stop()

if data.empty:
    st.info("No weather records yet. Run main.py first.")
    st.stop()

st.subheader("Latest saved temperatures")

latest = (
    data.sort_values("weather_time_utc")
    .drop_duplicates(subset="city", keep="last")
    .sort_values("city")
)

columns = st.columns(len(latest))

for column, (_, row) in zip(columns, latest.iterrows()):
    with column:
        st.metric(
            label=row["city"],
            value=f"{row['temperature_c']:.1f} °C",
        )
        st.caption(
            row["weather_time_utc"].strftime("%Y-%m-%d %H:%M UTC")
        )

st.subheader("Temperature history")

st.line_chart(
    data,
    x="weather_time_utc",
    y="temperature_c",
    color="city",
    x_label="Weather time (UTC)",
    y_label="Temperature (°C)",
)

st.subheader("Stored records")

st.dataframe(
    data.sort_values("weather_time_utc", ascending=False),
    hide_index=True,
)
