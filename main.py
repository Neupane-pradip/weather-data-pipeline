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
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()

    data = response.json()
    print(data)

    current_weather = data["current"]
    temperature = current_weather["temperature_2m"]

    print(f"Temperature in {city}: {temperature} °C")

if __name__ == "__main__":
    main()