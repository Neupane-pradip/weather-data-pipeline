import requests

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

    current_weather = data["current"]

    weather_record = {
        "city": city,
        "weather_time_utc": current_weather["time"],
        "temperature_c": current_weather["temperature_2m"],
        "source": "open-meteo"
    }

    print(f"Weather record for {city}: {weather_record}")


if __name__ == "__main__":
    main()