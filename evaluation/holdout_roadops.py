import json
import sys
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from agent.orchestrator import run_roadops


BENCHMARK_PATH = BASE_DIR / "data" / "benchmark_frozen_v1.json"
OUTPUT_PATH = BASE_DIR / "outputs" / "holdout_roadops_v1.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def make_json_serializable(obj):
    if isinstance(obj, BaseModel):
        return obj.model_dump()

    if isinstance(obj, dict):
        return {
            key: make_json_serializable(value)
            for key, value in obj.items()
        }

    if isinstance(obj, list):
        return [
            make_json_serializable(value)
            for value in obj
        ]

    return obj


def main():
    benchmark = load_json(BENCHMARK_PATH)

    results = []

    for incident in benchmark:
        incident_id = incident["id"]

        if incident_id in {"A1", "A2", "A3", "A4"}:
            continue

        print(f"\n===== ROADOPS {incident_id} =====")

        roadops_result = run_roadops(
            incident_id=incident_id,
            report=incident["initial_report"]
        )

        results.append({
            "incident_id": incident_id,
            "expected_priority": incident["expected_priority"],
            "roadops": roadops_result
        })

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(
            make_json_serializable(results),
            f,
            indent=2
        )

    print(
        f"\nSaved holdout RoadOps results to: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()