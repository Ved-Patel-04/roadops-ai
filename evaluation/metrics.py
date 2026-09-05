import json
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

RESULTS_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "comparison_A1_A4_v4.json"
)

BENCHMARK_PATH = (
    PROJECT_ROOT
    / "data"
    / "benchmark.json"
)


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def normalize(text):
    """
    Normalize text for simple deterministic matching.
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def assessment_text(assessment):
    """
    Combine the important assessment fields into one searchable string.
    """
    parts = []

    parts.extend(assessment.get("identified_factors", []))
    parts.extend(assessment.get("recommended_actions", []))
    parts.extend(assessment.get("missing_information", []))

    parts.append(
        assessment.get("reasoning_summary", "")
    )

    return normalize(" ".join(parts))

def factual_claim_text(assessment):
    """
    Build text containing affirmative factual claims only.

    Statements expressing uncertainty, missing information,
    or explicit negation are excluded from unsupported-assumption
    scoring.
    """

    exclusion_terms = [
        "no information",
        "not provided",
        "not known",
        "unknown",
        "unclear",
        "missing",
        "whether",
        "does not",
        "do not",
        "cannot",
        "not establish",
        "not support",
        "absence of",
        "not reported",
        "unavailable",
        "not available",
        "are unavailable",
        "is unavailable",
    ]

    negation_terms = [
        " no ",
        " zero ",
        " without ",
        " none ",
        " not ",
    ]

    factual_parts = []

    for factor in assessment.get("identified_factors", []):
        factor_lower = f" {factor.lower()} "

        if any(
            term in factor_lower
            for term in exclusion_terms
        ):
            continue

        if any(
            term in factor_lower
            for term in negation_terms
        ):
            continue

        factual_parts.append(factor)

    return normalize(" ".join(factual_parts))

def phrase_match(expected_phrase, generated_text):
    """
    Basic deterministic phrase matching.

    First checks the full phrase.
    If that fails, checks whether most meaningful words
    from the expected phrase appear in the generated output.
    """

    expected = normalize(expected_phrase)
    generated = normalize(generated_text)

    if expected in generated:
        return True

    expected_words = [
        word
        for word in expected.split()
        if len(word) > 3
    ]

    if not expected_words:
        return False

    matched_words = sum(
        1
        for word in expected_words
        if word in generated
    )

    coverage = matched_words / len(expected_words)

    return coverage >= 0.6


def calculate_priority_accuracy(results):
    baseline_correct = 0
    roadops_correct = 0

    rows = []

    for result in results:

        expected = result["expected_priority"]

        baseline_priority = (
            result["baseline"]["priority"]
        )

        roadops_priority = (
            result["roadops"]["assessment"]["priority"]
        )

        baseline_match = (
            baseline_priority == expected
        )

        roadops_match = (
            roadops_priority == expected
        )

        baseline_correct += int(baseline_match)
        roadops_correct += int(roadops_match)

        rows.append({
            "incident_id": result["incident_id"],
            "expected": expected,
            "baseline": baseline_priority,
            "baseline_correct": baseline_match,
            "roadops": roadops_priority,
            "roadops_correct": roadops_match,
        })

    total = len(results)

    return {
        "rows": rows,
        "baseline_accuracy": (
            baseline_correct / total
        ),
        "roadops_accuracy": (
            roadops_correct / total
        ),
    }


def calculate_factor_recall(
    assessment,
    required_factors
):
    """
    Measures how many benchmark-required factors
    appear in the generated assessment.
    """

    if not required_factors:
        return 1.0, []

    generated = assessment_text(assessment)

    matched = []

    for factor in required_factors:
        if phrase_match(factor, generated):
            matched.append(factor)

    recall = len(matched) / len(required_factors)

    return recall, matched


def calculate_guidance_coverage(
    assessment,
    expected_guidance
):
    """
    Measures how much expected operational guidance
    appears in the assessment.
    """

    if not expected_guidance:
        return 1.0, []

    generated = assessment_text(assessment)

    matched = []

    for guidance in expected_guidance:
        if phrase_match(guidance, generated):
            matched.append(guidance)

    coverage = len(matched) / len(expected_guidance)

    return coverage, matched


def calculate_prohibited_matches(
    assessment,
    prohibited_assumptions
):
    """
    Detect prohibited assumptions only within factual claims.

    Missing-information fields and recommendations are excluded because
    referencing a possible condition is not necessarily an assertion
    that the condition exists.
    """

    generated = factual_claim_text(
        assessment
    )

    violations = []

    for assumption in prohibited_assumptions:
        if phrase_match(
            assumption,
            generated
        ):
            violations.append(
                assumption
            )

    return violations


def evaluate_system(
    assessment,
    benchmark_case
):

    factor_recall, matched_factors = (
        calculate_factor_recall(
            assessment,
            benchmark_case["required_factors"]
        )
    )

    guidance_coverage, matched_guidance = (
        calculate_guidance_coverage(
            assessment,
            benchmark_case["expected_guidance"]
        )
    )

    violations = calculate_prohibited_matches(
        assessment,
        benchmark_case["prohibited_assumptions"]
    )

    return {
        "factor_recall": factor_recall,
        "matched_factors": matched_factors,

        "guidance_coverage": guidance_coverage,
        "matched_guidance": matched_guidance,

        "prohibited_assumption_matches": violations,
        "prohibited_assumption_count": len(violations),
    }


def run_detailed_evaluation(
    results,
    benchmark
):

    benchmark_lookup = {
        case["id"]: case
        for case in benchmark
    }

    detailed_results = []

    for result in results:

        incident_id = result["incident_id"]

        benchmark_case = (
            benchmark_lookup[incident_id]
        )

        baseline_eval = evaluate_system(
            result["baseline"],
            benchmark_case
        )

        roadops_eval = evaluate_system(
            result["roadops"]["assessment"],
            benchmark_case
        )

        detailed_results.append({
            "incident_id": incident_id,
            "baseline": baseline_eval,
            "roadops": roadops_eval,
        })

    return detailed_results


def average_metric(
    evaluations,
    system,
    metric
):

    values = [
        result[system][metric]
        for result in evaluations
    ]

    return sum(values) / len(values)


def calculate_tool_usage(results):

    traffic_calls = 0
    weather_calls = 0
    sop_calls = 0

    for result in results:

        plan = result["roadops"]["tool_plan"]

        traffic_calls += int(
            plan["use_traffic"]
        )

        weather_calls += int(
            plan["use_weather"]
        )

        sop_calls += int(
            plan["use_sop"]
        )

    return {
        "traffic_calls": traffic_calls,
        "weather_calls": weather_calls,
        "sop_calls": sop_calls,
    }


if __name__ == "__main__":

    results = load_json(RESULTS_PATH)
    benchmark = load_json(BENCHMARK_PATH)

    priority = calculate_priority_accuracy(
        results
    )

    detailed = run_detailed_evaluation(
        results,
        benchmark
    )

    tools = calculate_tool_usage(results)

    print("\n--- PRIORITY RESULTS ---\n")

    for row in priority["rows"]:

        print(
            f'{row["incident_id"]}: '
            f'Expected={row["expected"]} | '
            f'Baseline={row["baseline"]} '
            f'({"PASS" if row["baseline_correct"] else "FAIL"}) | '
            f'RoadOps={row["roadops"]} '
            f'({"PASS" if row["roadops_correct"] else "FAIL"})'
        )

    print("\n--- PRIORITY ACCURACY ---")

    print(
        f'Baseline: '
        f'{priority["baseline_accuracy"] * 100:.1f}%'
    )

    print(
        f'RoadOps: '
        f'{priority["roadops_accuracy"] * 100:.1f}%'
    )

    print(
        "\n--- DETAILED CASE RESULTS ---"
    )

    for result in detailed:

        print(
            f'\n{result["incident_id"]}'
        )

        print(
            "  Baseline factor recall: "
            f'{result["baseline"]["factor_recall"] * 100:.1f}%'
        )

        print(
            "  RoadOps factor recall:  "
            f'{result["roadops"]["factor_recall"] * 100:.1f}%'
        )

        print(
            "  Baseline guidance coverage: "
            f'{result["baseline"]["guidance_coverage"] * 100:.1f}%'
        )

        print(
            "  RoadOps guidance coverage:  "
            f'{result["roadops"]["guidance_coverage"] * 100:.1f}%'
        )

        print(
            "  Baseline prohibited matches: "
            f'{result["baseline"]["prohibited_assumption_count"]}'
        )

        print(
            "  RoadOps prohibited matches:  "
            f'{result["roadops"]["prohibited_assumption_count"]}'
        )

        print(
            "  Baseline prohibited matches detail: "
            f'{result["baseline"]["prohibited_assumption_matches"]}'
        )

        print(
            "  RoadOps prohibited matches detail:  "
            f'{result["roadops"]["prohibited_assumption_matches"]}'
        )

    print(
        "\n--- AVERAGE QUALITY METRICS ---"
    )

    print(
        "Baseline factor recall: "
        f'{average_metric(detailed, "baseline", "factor_recall") * 100:.1f}%'
    )

    print(
        "RoadOps factor recall:  "
        f'{average_metric(detailed, "roadops", "factor_recall") * 100:.1f}%'
    )

    print(
        "Baseline guidance coverage: "
        f'{average_metric(detailed, "baseline", "guidance_coverage") * 100:.1f}%'
    )

    print(
        "RoadOps guidance coverage:  "
        f'{average_metric(detailed, "roadops", "guidance_coverage") * 100:.1f}%'
    )

    print(
        "\n--- ROADOPS TOOL USAGE ---"
    )

    print(
        f'Traffic: {tools["traffic_calls"]}'
    )

    print(
        f'Weather: {tools["weather_calls"]}'
    )

    print(
        f'SOP: {tools["sop_calls"]}'
    )