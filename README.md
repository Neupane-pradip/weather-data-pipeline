# Weather Data Pipeline

A learning project that fetches current weather data from the
[Open-Meteo API](https://open-meteo.com/), validates it, stores it in
PostgreSQL, and displays saved observations in Streamlit.

## Current pipeline

```text
Open-Meteo API -> Python -> PostgreSQL -> Streamlit dashboard
```

Each pipeline run:

1. Fetches the current temperature for Helsinki, London, and Berlin.
2. Retries temporary API failures such as `429`, `500`, `502`, `503`, and `504`.
3. Validates the temperature and converts the API timestamp to UTC.
4. Inserts the observation into PostgreSQL.
5. Skips duplicate city, timestamp, and source combinations.
6. Logs progress and errors to the console and `pipeline.log`.
7. Continues processing the other cities when one city fails.

## Project structure

```text
.
├── main.py                 # Weather collection pipeline
├── dashboard.py            # Streamlit dashboard
├── test_retries.py         # Retry behavior test
├── sql/
│   └── schema.sql          # PostgreSQL table definition
├── .env.example            # Database configuration template
└── pipeline.log            # Generated runtime log
```

## Requirements

- Python 3.10 or newer
- PostgreSQL
- Internet access

Install the Python packages:

```powershell
python -m pip install requests psycopg[binary] python-dotenv pandas streamlit
```

## Setup

Create a PostgreSQL database named `weather_pipeline`, then run the schema:

```powershell
psql -U postgres -d weather_pipeline -f sql\schema.sql
```

Copy `.env.example` to `.env` and update the database password:

```powershell
Copy-Item .env.example .env
```

The `.env` file contains the `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, and
`DB_PASSWORD` values used by both `main.py` and `dashboard.py`. Do not commit
`.env` because it contains local credentials.

## Run the pipeline

```powershell
python main.py
```

The process exits with `0` when all cities succeed and `1` when one or more
cities fail.

## Open the Streamlit dashboard

Run the pipeline at least once, then start the dashboard:

```powershell
streamlit run dashboard.py
```

The dashboard displays:

- Latest saved temperature for each city
- UTC timestamp for each latest observation
- Temperature history chart
- All stored records in a table

The **Refresh saved data** button reruns the dashboard query and displays the
latest records from PostgreSQL.

## Run the test

The retry test uses a local temporary HTTP server and does not require
PostgreSQL or the Open-Meteo API:

```powershell
python -m unittest test_retries.py
```

## Scheduling

The pipeline can be run every 15 minutes with Windows Task Scheduler. The
computer must be awake, PostgreSQL must be running, and internet access must be
available. Missed weather timestamps are not automatically backfilled.

## Database design

The `weather_observations` table stores the city, UTC weather timestamp,
temperature in Celsius, source, and database collection time. Its unique
constraint on `(city, weather_time_utc, source)` prevents duplicate
observations.

## Future improvements

- Automatic scheduling configuration stored in the repository
- Historical backfilling
- Additional weather fields such as humidity, wind speed, or conditions
- Retry handling for database operations