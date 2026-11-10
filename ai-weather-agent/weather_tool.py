import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_weather(city: str, country: str = "") -> str:
    """
    Query real-time weather.
    :param city: City name, e.g., 'Tokyo'
    :param country: ISO country code, e.g., 'JP', 'US', 'CN'
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    location = f"{city},{country}" if country else city
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": location,
        "appid": api_key,
        "units": "metric",
        "lang": "zh_cn"  # Returns Chinese weather descriptions
    }
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if resp.status_code == 200:
            desc = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            feels = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            return f"{city} current weather: {desc}, temperature {temp}°C, feels like {feels}°C, humidity {humidity}%."
        elif resp.status_code == 404:
            return f"City not found: {location}. Please check whether the city or country code is correct."
        else:
            return f"Query failed (HTTP {resp.status_code})."
    except Exception as e:
        return f"Request error: {str(e)}"