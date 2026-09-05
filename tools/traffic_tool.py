import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TRAFFIC_DATA_PATH = PROJECT_ROOT / "data" / "traffic_context.json"


def get_traffic_context(incident_id: str) -> dict:
    """
    Retrieve deterministic traffic context for a benchmark incident.

    In the POC, this simulates an external traffic-data provider.
    A production implementation could replace this data source with
    a live traffic API without changing the tool interface.
    """

    with open(TRAFFIC_DATA_PATH, "r") as file:
        traffic_data = json.load(file)

    if incident_id not in traffic_data:
        return {
            "available": False,
            "message": "No traffic context available for this incident."
        }

    return {
        "available": True,
        "data": traffic_data[incident_id]
    }


if __name__ == "__main__":
    result = get_traffic_context("A3")
    print(json.dumps(result, indent=2))