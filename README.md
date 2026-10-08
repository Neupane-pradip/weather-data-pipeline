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

## Next steps

- Retry temporary API failures
- Schedule regular weather collection
- Build a Streamlit dashboard