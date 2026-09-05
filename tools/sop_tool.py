import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
SOP_PATH = BASE_DIR / "knowledge" / "roadops_sop.md"


def load_sop_text():
    with open(SOP_PATH, "r", encoding="utf-8") as f:
        return f.read()


def split_sections(text):
    return [
        section.strip()
        for section in text.split("---")
        if section.strip()
    ]


def get_priority_framework(sections):
    """
    Collect the complete RoadOps priority framework.

    The markdown file separates LOW, MEDIUM, HIGH, and CRITICAL
    into different sections, so they must be collected together.
    """

    priority_headings = (
        "## LOW",
        "## MEDIUM",
        "## HIGH",
        "## CRITICAL",
        "## INSUFFICIENT_INFORMATION",
    )

    framework_sections = []

    for section in sections:
        stripped = section.strip()

        if (
            "RoadOps POC Priority Framework" in stripped
            or stripped.startswith(priority_headings)
        ):
            framework_sections.append(section)

    if not framework_sections:
        return None

    return "\n\n---\n\n".join(framework_sections)


def keyword_score(query, section):
    query_words = {
        word.lower()
        for word in re.findall(r"\b\w+\b", query)
        if len(word) > 3
    }

    section_lower = section.lower()

    score = 0

    for word in query_words:
        if word in section_lower:
            score += 1

    return score


def get_sop_guidance(query, top_k=3):
    sop_text = load_sop_text()
    sections = split_sections(sop_text)

    priority_framework = get_priority_framework(sections)

    scored_sections = []

    priority_headings = (
        "## LOW",
        "## MEDIUM",
        "## HIGH",
        "## CRITICAL",
        "## INSUFFICIENT_INFORMATION",
    )

    for section in sections:

        stripped = section.strip()

        # Priority framework is always included separately
        if (
            "RoadOps POC Priority Framework" in stripped
            or stripped.startswith(priority_headings)
        ):
            continue

        score = keyword_score(query, section)

        if score > 0:
            scored_sections.append(
                (score, section)
            )

    scored_sections.sort(
        key=lambda item: item[0],
        reverse=True
    )

    dynamic_sections = [
        section
        for _, section in scored_sections[:top_k]
    ]

    guidance = []

    if priority_framework:
        guidance.append(priority_framework)

    guidance.extend(dynamic_sections)

    return {
        "available": len(guidance) > 0,
        "guidance": guidance
    }


if __name__ == "__main__":
    test_query = (
        "disabled vehicle active lane blockage "
        "moderate traffic small queue"
    )

    result = get_sop_guidance(test_query)

    print(result)