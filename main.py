import os
from pathlib import Path
from datetime import datetime, timezone

import requests
import psycopg
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

def transform_weather(data, city):
    current_weather = data["current"]

    temperature = current_weather["temperature_2m"]

    if temperature is None:
        raise ValueError("Temperature is missing from the API response.")

    weather_time = datetime.fromisoformat(current_weather["time"])
    weather_time = weather_time.replace(tzinfo=timezone.utc)

    weather_record = {
        "city": city,
        "weather_time_utc": weather_time,
        "temperature_c": float(temperature),
        "source": "open-meteo",
    }

    return weather_record

def save_weather(weather_record):
    query = """
        INSERT INTO weather_observations (
            city,
            weather_time_utc,
            temperature_c,
            source
        )
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (city, weather_time_utc, source) DO NOTHING
        RETURNING id;
    """

    values = (
        weather_record["city"],
        weather_record["weather_time_utc"],
        weather_record["temperature_c"],
        weather_record["source"],
    )

    with psycopg.connect(
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        connect_timeout=10,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, values)
            inserted_row = cursor.fetchone()

    if inserted_row is None:
        return None

    return inserted_row[0]

def main():
    print("Weather pipeline project started!")

    city = "Helsinki"
    latitude = 60.1699
    longitude = 24.9384
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m",
        "temperature_unit": "celsius",
        "timezone": "GMT",
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()

    data = response.json()

    weather_record = transform_weather(data, city)

    record_id = save_weather(weather_record)

    if record_id is None:
        print("Record already exists; skipped duplicate.")
    else:
        print(f"Weather record saved with ID: {record_id}")

    print(f"Weather record for {city}: {weather_record}")
    print("Timestamp type:", type(weather_record["weather_time_utc"]))
    print("Temperature type:", type(weather_record["temperature_c"]))


if __name__ == "__main__":
    main()