import os
from pathlib import Path
from datetime import datetime, timezone
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import requests
import psycopg
import logging
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            Path(__file__).resolve().parent / "pipeline.log",
            encoding="utf-8",
        ),
    ],
)

logger = logging.getLogger(__name__)

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

def fetch_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m",
        "temperature_unit": "celsius",
        "timezone": "GMT",
    }

    retry_policy = Retry(
        total=2,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        respect_retry_after_header=True,
        raise_on_status=False,
    )

    adapter = HTTPAdapter(max_retries=retry_policy)

    with requests.Session() as session:
        session.mount("https://", adapter)

        response = session.get(url, params=params, timeout=20)
        response.raise_for_status()

        return response.json()

def main():
    logger.info("Weather pipeline started.")

    cities = [
        {
            "name": "Helsinki",
            "latitude": 60.1699,
            "longitude": 24.9384,
        },
        {
            "name": "London",
            "latitude": 51.5074,
            "longitude": -0.1278,
        },
        {
            "name": "Berlin",
            "latitude": 52.5200,
            "longitude": 13.4050,
        },
    ]

    inserted_count = 0
    skipped_count = 0
    failed_count = 0

    for city in cities:
        city_name = city["name"]
        logger.info("Fetching weather for %s...", city_name)

        try:
            data = fetch_weather(
                city["latitude"],
                city["longitude"],
            )

            weather_record = transform_weather(data, city_name)
            record_id = save_weather(weather_record)

        except requests.exceptions.RequestException:
            failed_count += 1
            logger.exception("%s: API request failed.", city_name)
            continue

        except psycopg.Error:
            failed_count += 1
            logger.exception("%s: database operation failed.", city_name)
            continue

        except (KeyError, ValueError, TypeError):
            failed_count += 1
            logger.exception(
                "%s: invalid data or missing configuration.",
                city_name,
            )
            continue

        if record_id is None:
            skipped_count += 1
            logger.info("%s: skipped duplicate.", city_name)
        else:
            inserted_count += 1
            logger.info(
                "%s: saved record ID %s.",
                city_name,
                record_id,
            )

    logger.info(
        "Batch finished: %s inserted, %s skipped, %s failed.",
        inserted_count,
        skipped_count,
        failed_count,
    )

    return 1 if failed_count else 0

if __name__ == "__main__":
    raise SystemExit(main())