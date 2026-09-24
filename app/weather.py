from datetime import date

import requests


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def get_weather(
    latitude: float,
    longitude: float,
    target_date: date,
) -> dict:

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": (
            "temperature_2m_max,"
            "temperature_2m_min,"
            "temperature_2m_mean,"
            "sunshine_duration,"
            "precipitation_sum"
        ),
        "timezone": "auto",
        "start_date": target_date.isoformat(),
        "end_date": target_date.isoformat(),
    }

    response = requests.get(
        OPEN_METEO_URL,
        params=params,
        timeout=15,
    )

    response.raise_for_status()

    data = response.json()

    if "daily" not in data:
        raise RuntimeError("Weather API returned no daily data.")

    daily = data["daily"]

    if not daily.get("time"):
        raise RuntimeError(
            f"No weather data available for {target_date}."
        )

    max_temp = daily["temperature_2m_max"][0]
    min_temp = daily["temperature_2m_min"][0]
    mean_temp = daily["temperature_2m_mean"][0]

    sunshine_seconds = daily["sunshine_duration"][0]
    precipitation = daily["precipitation_sum"][0]

    sunshine_hours = (
        sunshine_seconds / 3600
        if sunshine_seconds is not None
        else None
    )

    return {
        "date": daily["time"][0],
        "temperature_max": max_temp,
        "temperature_min": min_temp,
        "temperature_mean": mean_temp,
        "sunshine_sum": sunshine_hours,
        "precipitation_sum": precipitation,
    }