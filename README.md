# Weather Data Pipeline

A learning project that collects weather data using Python,
stores observations in PostgreSQL, and displays them in Streamlit.

## Planned features

- Fetch weather data from an API
- Clean and validate weather observations
- Store observations in PostgreSQL
- Collect weather for multiple cities on a schedule
- Display weather trends in Streamlit

## Implemented features

- Fetch current temperature for Helsinki, London, and Berlin
- Validate missing temperatures and prepare UTC timestamps
- Store weather records in PostgreSQL
- Skip duplicate city, timestamp, and source combinations
- Log batch progress to the console and pipeline.log
- Handle per-city errors and report batch totals

## Current pipeline

Open-Meteo API → Python → PostgreSQL

## Scheduled collection

The pipeline runs every 15 minutes using Windows Task Scheduler.

Each run:
- Fetches weather for Helsinki, London, and Berlin
- Validates and transforms the response
- Stores new records in PostgreSQL
- Skips duplicate records
- Writes progress and errors to pipeline.log

The local setup requires the computer to be awake, the user
to be logged in, PostgreSQL to be running, and internet access.

Missed weather timestamps are not automatically backfilled.

## Next steps
- Build a Streamlit dashboard