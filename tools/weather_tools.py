#done
import httpx
from typing import Dict, Any

_coordinates_cache: Dict[str, Dict[str, Any]] = {}

async def _get_coordinates(city: str, client: httpx.AsyncClient) -> dict:
    """Helper to fetch coordinates using a shared client and cache results."""
    city_key = city.strip().lower()
    if city_key in _coordinates_cache:
        return _coordinates_cache[city_key]

    try:
        response = await client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json",
            },
            timeout=10.0,
        )
        response.raise_for_status()
        data = response.json()
    except httpx.HTTPError as e:
        return {"error": f"Geocoding API error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error during geocoding: {str(e)}"}

    if not data.get("results"):
        return {"error": f"Location '{city}' was not found."}

    location = data["results"][0]
    result = {
        "name": location["name"],
        "country": location.get("country"),
        "latitude": location["latitude"],
        "longitude": location["longitude"],
    }
    _coordinates_cache[city_key] = result
    return result


async def get_coordinates(city: str) -> dict:
    """Get coordinates (latitude, longitude, name, country) for a city."""
    async with httpx.AsyncClient() as client:
        return await _get_coordinates(city, client)


async def _get_current_weather(location: dict, client: httpx.AsyncClient) -> dict:
    """Helper to fetch current weather using a shared client."""
    try:
        response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "current": [
                    "temperature_2m",
                    "apparent_temperature",
                    "relative_humidity_2m",
                    "precipitation",
                    "wind_speed_10m",
                ],
                "timezone": "auto",
            },
            timeout=10.0,
        )
        response.raise_for_status()
        current = response.json()["current"]
    except httpx.HTTPError as e:
        return {"error": f"Weather API error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error during weather lookup: {str(e)}"}

    return {
        "city": location["name"],
        "country": location.get("country"),
        "temperature_c": current["temperature_2m"],
        "feels_like_c": current["apparent_temperature"],
        "humidity_percent": current["relative_humidity_2m"],
        "precipitation_mm": current["precipitation"],
        "wind_speed_kmh": current["wind_speed_10m"],
    }


async def get_current_weather(city: str) -> dict:
    """Get the current weather conditions for a city."""
    print("function called[get_current_weather]")
    async with httpx.AsyncClient() as client:
        location = await _get_coordinates(city, client)
        if "error" in location:
            return location
        return await _get_current_weather(location, client)


async def _get_weather_forecast(location: dict, days: int, client: httpx.AsyncClient) -> dict:
    """Helper to fetch daily forecast using a shared client."""
    days = max(1, min(days, 7))

    try:
        response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "daily": [
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "precipitation_probability_max",
                    "weather_code",
                ],
                "forecast_days": days,
                "timezone": "auto",
            },
            timeout=10.0,
        )
        response.raise_for_status()
        daily = response.json()["daily"]
    except httpx.HTTPError as e:
        return {"error": f"Forecast API error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error during forecast lookup: {str(e)}"}

    forecast = []
    for i in range(len(daily["time"])):
        forecast.append({
            "date": daily["time"][i],
            "max_temperature_c": daily["temperature_2m_max"][i],
            "min_temperature_c": daily["temperature_2m_min"][i],
            "rain_probability_percent": daily["precipitation_probability_max"][i],
            "weather_code": daily["weather_code"][i],
        })

    return {
        "city": location["name"],
        "country": location.get("country"),
        "forecast": forecast,
    }


async def get_weather_forecast(city: str, days: int = 7) -> dict:
    """Get a daily weather forecast for a city for up to 7 days."""
    async with httpx.AsyncClient() as client:
        location = await _get_coordinates(city, client)
        if "error" in location:
            return location
        return await _get_weather_forecast(location, days, client)


async def get_rain_forecast(city: str, days: int = 3) -> dict:
    """Check rain probability for a city over the next few days."""
    print("function called[rain forecast]")
    async with httpx.AsyncClient() as client:
        location = await _get_coordinates(city, client)
        if "error" in location:
            return location
        forecast_data = await _get_weather_forecast(location, days, client)

        if "error" in forecast_data:
            return forecast_data

        rain_data = []
        for day in forecast_data["forecast"]:
            rain_data.append({
                "date": day["date"],
                "rain_probability_percent": day["rain_probability_percent"],
            })

        return {
            "city": forecast_data["city"],
            "rain_forecast": rain_data,
        }
