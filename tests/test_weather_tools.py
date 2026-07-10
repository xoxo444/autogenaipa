import asyncio
import time
from tools.weather_tools import (
    get_current_weather,
    get_weather_forecast,
    get_rain_forecast,
    _coordinates_cache,
)


async def main():
    print("--- Testing get_current_weather ---")
    london_current = await get_current_weather("London")
    print(f"London Current Weather: {london_current}")

    print("\n--- Testing get_weather_forecast ---")
    london_forecast = await get_weather_forecast("London", days=3)
    print(f"London 3-day Forecast: {london_forecast}")

    print("\n--- Testing get_rain_forecast ---")
    london_rain = await get_rain_forecast("London", days=3)
    print(f"London Rain Forecast: {london_rain}")

    print("\n--- Testing Coordinate Cache ---")
    print(f"Initial Cache state: {list(_coordinates_cache.keys())}")
    
    # Measure time for a cached city lookup
    start_time = time.perf_counter()
    # "London" should be cached now, so this lookup should be extremely fast and not make a geocoding API request
    london_forecast_cached = await get_weather_forecast("London", days=1)
    cached_duration = time.perf_counter() - start_time
    print(f"Cached lookup took {cached_duration:.4f} seconds.")
    assert "london" in _coordinates_cache

    print("\n--- Testing Error Handling for non-existent city ---")
    error_result = await get_current_weather("ThisCityDefinitelyDoesNotExist123456")
    print(f"Non-existent city response: {error_result}")
    assert "error" in error_result

    print("\n--- ALL TESTS PASSED SUCCESSFULLY! ---")


if __name__ == "__main__":
    asyncio.run(main())
