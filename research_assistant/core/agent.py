# agent.py
import os
import requests
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.function_tool import FunctionTool

load_dotenv('/home/nikunjagrwl/Documents/Research-assistant/.env')
api_key = os.getenv("GOOGLE_API_KEY")

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

# Create weather tool directly without MCP overhead
weather_tool = FunctionTool(get_weather)

root_agent = LlmAgent( 
    name="weather_agent",
    model="gemini-1.5-flash",
    description="An agent that provides weather info.",
    instruction=(
        "You are a helpful assistant. When the user asks about weather, "
        "use the `get_weather` tool with a city name."
    ),
    tools=[weather_tool],
)