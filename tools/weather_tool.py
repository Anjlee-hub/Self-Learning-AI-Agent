import json
import urllib.error
import urllib.parse
import urllib.request


WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Light rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Light snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Heavy thunderstorm with hail",
}


def _fetch_json(url):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def _weather_condition(code):
    return WEATHER_CODES.get(code, "Unknown condition")


def get_weather(location):
    cleaned = (location or "").strip()
    if not cleaned:
        return {
            "success": False,
            "error": "No location was provided for the weather lookup.",
        }

    try:
        geocode_url = (
            "https://geocoding-api.open-meteo.com/v1/search?"
            f"name={urllib.parse.quote(cleaned)}&count=1&language=en&format=json"
        )
        geocode = _fetch_json(geocode_url)
    except (urllib.error.URLError, TimeoutError, ValueError):
        return {
            "success": False,
            "error": "Weather service is unavailable right now. Please try again later.",
        }

    results = geocode.get("results") or []
    if not results:
        return {
            "success": False,
            "error": f"Could not find weather information for '{cleaned}'.",
        }

    place = results[0]
    lat = place.get("latitude")
    lon = place.get("longitude")
    location_name = place.get("name") or cleaned
    country = place.get("country") or ""
    display_name = f"{location_name}, {country}" if country else location_name

    try:
        weather_url = (
            "https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            "&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code"
            "&timezone=auto"
        )
        weather = _fetch_json(weather_url)
    except (urllib.error.URLError, TimeoutError, ValueError):
        return {
            "success": False,
            "error": "Weather service is unavailable right now. Please try again later.",
        }

    current = weather.get("current") or {}
    temp = current.get("temperature_2m")
    humidity = current.get("relative_humidity_2m")
    wind = current.get("wind_speed_10m")
    condition = _weather_condition(current.get("weather_code"))

    return {
        "success": True,
        "location": display_name,
        "temperature": temp,
        "weather_condition": condition,
        "humidity": humidity,
        "wind_speed": wind,
        "source": "Open-Meteo",
    }


def format_weather_response(weather_result):
    if not weather_result or not weather_result.get("success"):
        return weather_result.get("error", "Weather information is unavailable.") if weather_result else "Weather information is unavailable."

    location = weather_result.get("location", "Unknown location")
    temp = weather_result.get("temperature")
    condition = weather_result.get("weather_condition", "Unknown condition")
    humidity = weather_result.get("humidity")
    wind = weather_result.get("wind_speed")

    summary_parts = [
        f"Weather for {location}: {temp}°C, {condition}",
    ]

    if humidity is not None:
        summary_parts.append(f"Humidity: {humidity}%")

    if wind is not None:
        summary_parts.append(f"Wind: {wind} km/h")

    summary_parts.append("(source: Open-Meteo weather tool)")
    return ". ".join(summary_parts)
