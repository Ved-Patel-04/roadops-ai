import json
import sys
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent

# Add project root to Python import path
sys.path.insert(0, str(BASE_DIR))

from agent.orchestrator import run_roadops

BENCHMARK_PATH = BASE_DIR / "data" / "benchmark.json"
FROZEN_V1_PATH = BASE_DIR / "outputs" / "comparison_A1_A4_v1.json"
OUTPUT_PATH = BASE_DIR / "outputs" / "comparison_A1_A4_v4.json"


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
    frozen_v1 = load_json(FROZEN_V1_PATH)

    # Map frozen baseline results by incident id
    frozen_baselines = {
        item["incident_id"]: item["baseline"]
        for item in frozen_v1
    }

    results = []

    for incident in benchmark:
        incident_id = incident["id"]

        if incident_id not in {"A1", "A2", "A3", "A4"}:
            continue

        print("\n" + "=" * 60)
        print(f"RUNNING INCIDENT {incident_id}")
        print("=" * 60)

        print("\nUsing frozen baseline...")

        baseline_result = frozen_baselines[incident_id]

        print("\nRunning RoadOps...")

        roadops_result = run_roadops(
            incident_id=incident_id,
            report=incident["initial_report"]
        )

        results.append(
            {
                "incident_id": incident_id,
                "expected_priority": incident["expected_priority"],
                "baseline": baseline_result,
                "roadops": roadops_result
            }
        )

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(
            make_json_serializable(results),
            f,
            indent=2
        )

    print("\n" + "=" * 60)
    print("COMPARISON COMPLETE")
    print("=" * 60)

    print("\nResults saved to:")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()