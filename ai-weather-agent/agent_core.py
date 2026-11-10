import os
import json
from datetime import datetime, timezone
from functools import lru_cache

import requests
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

load_dotenv()

OWM = "https://api.openweathermap.org/data/2.5"
NOMINATIM = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "SkylineWeather/1.0 (personal project)"}  # required by Nominatim


def _local(ts: int, tz: int) -> datetime:
    """Unix timestamp -> the place's local wall-clock time (tz = offset in seconds)."""
    return datetime.fromtimestamp(ts + tz, tz=timezone.utc)


def _label(dt: datetime) -> str:
    h = dt.hour
    return f"{h % 12 or 12} {'AM' if h < 12 else 'PM'}"


@lru_cache(maxsize=256)
def _geocode(query: str):
    """Find ANY place (city, region, valley, landmark, village) via OpenStreetMap.
    Returns (lat, lon, name, region_label) or None."""
    try:
        r = requests.get(
            NOMINATIM,
            params={"q": query, "format": "jsonv2", "limit": 1,
                    "addressdetails": 1, "accept-language": "en"},
            headers=HEADERS, timeout=10,
        )
        hits = r.json() if r.status_code == 200 else []
        if not hits:
            return None
        h = hits[0]
        addr = h.get("address", {})
        name = h.get("name") or h.get("display_name", "").split(",")[0] or query
        cc = addr.get("country_code", "").upper()
        state = addr.get("state") or addr.get("region") or ""
        parts = [p for p in (state if state != name else "", cc) if p]
        return float(h["lat"]), float(h["lon"]), name, ", ".join(parts)
    except Exception:
        return None


def get_weather_data(query: str) -> dict:
    """Weather + 24h forecast for any place the user types."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    query = (query or "").strip()
    if not query:
        return {"error": "Enter a place to search."}

    # "Kashmir & Ladakh" -> show the first place and tell the user about the rest
    note = ""
    if "&" in query:
        first, *rest = [p.strip() for p in query.split("&") if p.strip()]
        if rest:
            note = f"Showing {first}. Search {', '.join(rest)} on its own to see it."
            query = first

    geo = _geocode(query)
    if geo:
        lat, lon, name, region = geo
        params = {"lat": lat, "lon": lon, "appid": api_key, "units": "metric"}
    else:
        # Fallback: OpenWeather's own city lookup
        name, region = None, None
        params = {"q": query, "appid": api_key, "units": "metric"}

    try:
        resp = requests.get(f"{OWM}/weather", params=params, timeout=10)
        data = resp.json()
        if resp.status_code != 200:
            return {"error": f"Couldn\u2019t find \u201c{query}\u201d. Try adding a country, like \u201c{query}, India\u201d."}

        tz = data.get("timezone", 0)
        temp = round(data["main"]["temp"])
        condition = data["weather"][0]["main"]

        hourly = [{"time": "Now", "temp": temp, "condition": condition}]
        temps = [temp]
        try:
            fr = requests.get(f"{OWM}/forecast", params={**params, "cnt": 8}, timeout=10)
            if fr.status_code == 200:
                items = fr.json()["list"]
                temps += [round(i["main"]["temp"]) for i in items]
                for i in items[:7]:
                    hourly.append({
                        "time": _label(_local(i["dt"], tz)),
                        "temp": round(i["main"]["temp"]),
                        "condition": i["weather"][0]["main"],
                    })
        except Exception:
            pass  # forecast is optional; the page falls back to an estimate

        out = {
            "city": name or data.get("name") or query,
            "country": region if region is not None else data.get("sys", {}).get("country", ""),
            "temp": temp,
            "feels_like": round(data["main"]["feels_like"]),
            "humidity": data["main"]["humidity"],
            "wind": round(data["wind"]["speed"] * 3.6),  # m/s -> km/h
            "high": max(temps),
            "low": min(temps),
            "condition": condition,
            "description": data["weather"][0]["description"],
            "local_time": _local(data["dt"], tz).strftime("%H:%M"),
            "sunrise": _local(data["sys"]["sunrise"], tz).strftime("%H:%M"),
            "sunset": _local(data["sys"]["sunset"], tz).strftime("%H:%M"),
            "hourly": hourly,
        }
        if note:
            out["note"] = note
        return out
    except Exception as e:
        return {"error": str(e)}


def get_weather_json(query: str) -> str:
    return json.dumps(get_weather_data(query))


# ---- Optional LLM agent (no longer used by app.py; kept for reference) ----
class WeatherInput(BaseModel):
    city: str = Field(description="The place exactly as the user typed it: city, region, village or landmark")
    country: str = Field(description="Country code", default="")


@tool("get_weather", args_schema=WeatherInput)
def weather_tool(city: str, country: str = "") -> str:
    """Query real-time weather and hourly forecast for any place, and return JSON."""
    return get_weather_json(f"{city}, {country}" if country else city)


llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0)
system_prompt = """You are a weather API.
When the user asks for weather, call the `get_weather` tool with the place exactly as the user typed it.
You MUST output the exact JSON string returned by the tool, character for character. No extra text, markdown, or code blocks."""
agent = create_agent(model=llm, tools=[weather_tool], system_prompt=system_prompt)