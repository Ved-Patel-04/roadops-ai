import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
WEATHER_DATA_PATH = PROJECT_ROOT / "data" / "weather_context.json"


def get_weather_context(incident_id: str) -> dict:
    """
    Retrieve deterministic weather context for a benchmark incident.
    """

    with open(WEATHER_DATA_PATH, "r") as file:
        weather_data = json.load(file)

    if incident_id not in weather_data:
        return {
            "available": False,
            "message": "No weather context available for this incident."
        }

    return {
        "available": True,
        "data": weather_data[incident_id]
    }


if __name__ == "__main__":
    result = get_weather_context("A3")
    print(json.dumps(result, indent=2))