import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DETAILS_PATH = (
    BASE_DIR
    / "data"
    / "incident_details.json"
)


def get_incident_details(incident_id):
    """
    Retrieve structured incident information from the
    synthetic incident-management data source.
    """

    with open(
        DETAILS_PATH,
        "r",
        encoding="utf-8"
    ) as f:
        data = json.load(f)

    incident = data.get(incident_id)

    if incident is None:
        return {
            "available": False,
            "data": None
        }

    return {
        "available": True,
        "data": incident
    }


if __name__ == "__main__":
    result = get_incident_details("A4")

    print(
        json.dumps(
            result,
            indent=2
        )
    )