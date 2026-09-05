import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from evaluation.metrics import (
    calculate_factor_recall,
    calculate_guidance_coverage,
    calculate_prohibited_matches,
)


BENCHMARK_PATH = BASE_DIR / "data" / "benchmark_frozen_v1.json"
BASELINE_PATH = BASE_DIR / "outputs" / "holdout_baseline_v1.json"
ROADOPS_PATH = BASE_DIR / "outputs" / "holdout_roadops_v1.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    benchmark = load_json(BENCHMARK_PATH)
    baseline_results = load_json(BASELINE_PATH)
    roadops_results = load_json(ROADOPS_PATH)

    benchmark_map = {
        item["id"]: item
        for item in benchmark
        if item["id"] not in {"A1", "A2", "A3", "A4"}
    }

    baseline_map = {
        item["incident_id"]: item["baseline"]
        for item in baseline_results
    }

    roadops_map = {
        item["incident_id"]: item["roadops"]
        for item in roadops_results
    }

    total_cases = 0

    baseline_priority_correct = 0
    roadops_priority_correct = 0

    baseline_factor_scores = []
    roadops_factor_scores = []

    baseline_guidance_scores = []
    roadops_guidance_scores = []

    baseline_prohibited_total = 0
    roadops_prohibited_total = 0

    traffic_calls = 0
    weather_calls = 0
    incident_details_calls = 0
    sop_calls = 0

    print("\n--- HOLDOUT PRIORITY RESULTS ---\n")

    for incident_id, case in benchmark_map.items():
        baseline = baseline_map[incident_id]
        roadops = roadops_map[incident_id]
        roadops_assessment = roadops["assessment"]

        expected = case["expected_priority"]

        baseline_priority = baseline["priority"]
        roadops_priority = roadops_assessment["priority"]

        baseline_pass = baseline_priority == expected
        roadops_pass = roadops_priority == expected

        baseline_priority_correct += int(baseline_pass)
        roadops_priority_correct += int(roadops_pass)
        total_cases += 1

        print(
            f"{incident_id}: Expected={expected} | "
            f"Baseline={baseline_priority} "
            f"({'PASS' if baseline_pass else 'FAIL'}) | "
            f"RoadOps={roadops_priority} "
            f"({'PASS' if roadops_pass else 'FAIL'})"
        )

        baseline_factor = calculate_factor_recall(
            baseline,
            case["required_factors"]
        )[0]

        roadops_factor = calculate_factor_recall(
            roadops_assessment,
            case["required_factors"]
        )[0]

        baseline_guidance = calculate_guidance_coverage(
            baseline,
            case["expected_guidance"]
        )[0]

        roadops_guidance = calculate_guidance_coverage(
            roadops_assessment,
            case["expected_guidance"]
        )[0]

        baseline_prohibited = calculate_prohibited_matches(
            baseline,
            case["prohibited_assumptions"]
        )

        roadops_prohibited = calculate_prohibited_matches(
            roadops_assessment,
            case["prohibited_assumptions"]
        )

        if baseline_prohibited:
            print(
                f"  Baseline prohibited detail: "
                f"{baseline_prohibited}"
            )

        if roadops_prohibited:
            print(
                f"  RoadOps prohibited detail: "
                f"{roadops_prohibited}"
            )

        baseline_factor_scores.append(baseline_factor)
        roadops_factor_scores.append(roadops_factor)

        baseline_guidance_scores.append(baseline_guidance)
        roadops_guidance_scores.append(roadops_guidance)

        baseline_prohibited_total += len(baseline_prohibited)
        roadops_prohibited_total += len(roadops_prohibited)

        tool_plan = roadops["tool_plan"]

        traffic_calls += int(tool_plan.get("use_traffic", False))
        weather_calls += int(tool_plan.get("use_weather", False))
        incident_details_calls += int(
            tool_plan.get("use_incident_details", False)
        )
        sop_calls += int(tool_plan.get("use_sop", False))

    baseline_priority_accuracy = (
        baseline_priority_correct / total_cases * 100
    )

    roadops_priority_accuracy = (
        roadops_priority_correct / total_cases * 100
    )

    baseline_factor_avg = (
        sum(baseline_factor_scores)
        / len(baseline_factor_scores)
    )

    roadops_factor_avg = (
        sum(roadops_factor_scores)
        / len(roadops_factor_scores)
    )

    baseline_guidance_avg = (
        sum(baseline_guidance_scores)
        / len(baseline_guidance_scores)
    )

    roadops_guidance_avg = (
        sum(roadops_guidance_scores)
        / len(roadops_guidance_scores)
    )

    print("\n--- HOLDOUT PRIORITY ACCURACY ---")
    print(f"Baseline: {baseline_priority_accuracy:.1f}%")
    print(f"RoadOps:  {roadops_priority_accuracy:.1f}%")

    print("\n--- HOLDOUT QUALITY METRICS ---")
    print(
        f"Baseline factor recall: "
        f"{baseline_factor_avg * 100:.1f}%"
    )
    print(
        f"RoadOps factor recall:  "
        f"{roadops_factor_avg * 100:.1f}%"
    )

    print(
        f"Baseline guidance coverage: "
        f"{baseline_guidance_avg * 100:.1f}%"
    )
    print(
        f"RoadOps guidance coverage:  "
        f"{roadops_guidance_avg * 100:.1f}%"
    )

    print(
        f"Baseline prohibited matches: "
        f"{baseline_prohibited_total}"
    )
    print(
        f"RoadOps prohibited matches:  "
        f"{roadops_prohibited_total}"
    )

    print("\n--- ROADOPS TOOL USAGE ---")
    print(f"Traffic: {traffic_calls}/{total_cases}")
    print(f"Weather: {weather_calls}/{total_cases}")
    print(
        f"Incident Details: "
        f"{incident_details_calls}/{total_cases}"
    )
    print(f"SOP: {sop_calls}/{total_cases}")


if __name__ == "__main__":
    main()