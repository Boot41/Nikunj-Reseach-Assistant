# /home/nikunjagrwl/Documents/Research-assistant/research_assistant/mcp/server.py
import requests
from fastmcp import FastMCP

app = FastMCP("weather_mcp")


@app.tool()
def get_weather(city: str) -> dict:
    """
    Get the current weather for a city using Open-Meteo (no API key needed).
    Returns temperature (C) and conditions.
    """
    # 1. Geocode city -> lat/lon
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_resp = requests.get(geo_url, params={"name": city, "count": 1})
    if geo_resp.status_code != 200 or not geo_resp.json().get("results"):
        return {"error": f"Could not find location for {city}"}

    location = geo_resp.json()["results"][0]
    lat, lon = location["latitude"], location["longitude"]

    # 2. Fetch current weather
    weather_url = "https://api.open-meteo.com/v1/forecast"
    weather_resp = requests.get(
        weather_url,
        params={
            "latitude": lat,
            "longitude": lon,
            "current_weather": True,
        },
    )
    if weather_resp.status_code != 200:
        return {"error": f"Weather API request failed for {city}"}

    current = weather_resp.json().get("current_weather", {})
    return {
        "city": location["name"],
        "latitude": lat,
        "longitude": lon,
        "temperature_c": current.get("temperature"),
        "windspeed": current.get("windspeed"),
        "weather_code": current.get("weathercode"),
    }


if __name__ == "__main__":
    app.run()
