import requests
from datetime import datetime, timezone

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

    print(f"Weather record for {city}: {weather_record}")
    print("Timestamp type:", type(weather_record["weather_time_utc"]))
    print("Temperature type:", type(weather_record["temperature_c"]))


if __name__ == "__main__":
    main()