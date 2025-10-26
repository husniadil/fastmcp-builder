"""
Weather Forecast Tool - External API Integration Example

Demonstrates how to integrate with external APIs in MCP tools.
Uses a mock weather service for demonstration purposes.
"""

import random
from datetime import datetime, timedelta
from fastmcp import Context


async def get_forecast(
    city: str = "Jakarta", days: int = 3, ctx: Context | None = None
) -> dict:
    """
    Get weather forecast for a city

    This tool demonstrates external API integration patterns.
    In production, replace the mock data with actual API calls.

    Args:
        city: City name (default: "Jakarta")
        days: Number of forecast days (1-7, default: 3, auto-clamped if out of bounds)
        ctx: FastMCP context (optional, for logging)

    Returns:
        Weather forecast data with temperature, conditions, and humidity

    Example:
        get_forecast("Tokyo", 5)
        # Returns 5-day forecast for Tokyo

    Production Usage:
        Replace mock data with real API:
        - OpenWeatherMap: https://openweathermap.org/api
        - WeatherAPI: https://www.weatherapi.com/
        - NOAA: https://www.weather.gov/documentation/services-web-api
    """
    # Validate inputs
    if days < 1 or days > 7:
        days = min(max(days, 1), 7)  # Clamp to 1-7

    if ctx:
        await ctx.info(f"🌤️  Fetching {days}-day forecast for {city}")

    # Mock weather data
    # In production: Replace with actual API call
    conditions = ["Sunny", "Partly Cloudy", "Cloudy", "Rainy", "Stormy"]

    forecast_data = []
    base_temp = random.randint(20, 30)  # Base temperature

    for day in range(days):
        date = datetime.now() + timedelta(days=day)
        temp_variation = random.randint(-5, 5)

        forecast_data.append(
            {
                "date": date.strftime("%Y-%m-%d"),
                "day_name": date.strftime("%A"),
                "temperature": {
                    "high": base_temp + temp_variation + random.randint(0, 3),
                    "low": base_temp + temp_variation - random.randint(3, 8),
                    "unit": "°C",
                },
                "condition": random.choice(conditions),
                "humidity": random.randint(40, 90),
                "precipitation_chance": random.randint(0, 100),
            }
        )

    if ctx:
        await ctx.info("✅ Forecast retrieved successfully")

    return {
        "status": "success",
        "city": city,
        "country": "N/A (mock data)",
        "forecast_days": days,
        "forecast": forecast_data,
        "note": "This is mock data. In production, integrate with a real weather API.",
        "suggested_apis": [
            "OpenWeatherMap (https://openweathermap.org/api)",
            "WeatherAPI (https://www.weatherapi.com/)",
            "NOAA (https://www.weather.gov/documentation/services-web-api)",
        ],
    }
