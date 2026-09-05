import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


# Add the project root to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from schemas.models import IncidentAssessment


# Load variables from .env
load_dotenv(PROJECT_ROOT / ".env")


# Create OpenAI client.
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


BASELINE_INSTRUCTIONS = """
You are evaluating roadway incident reports for a proof-of-concept
decision-support experiment.

You will receive ONLY the initial incident report.

Assess the incident using only information explicitly contained in the
report.

Do not assume facts that were not provided.

If important information is unavailable, list it under
missing_information.

If there is not enough evidence to make a reliable priority assessment,
use INSUFFICIENT_INFORMATION.

Priority must be one of:
LOW
MEDIUM
HIGH
CRITICAL
INSUFFICIENT_INFORMATION

Recommended actions should remain general decision-support suggestions.
Do not assume emergency personnel have already been dispatched.

The system is advisory only and does not make final operational
decisions.
"""


def assess_baseline(report: str) -> IncidentAssessment:
    response = client.responses.parse(
        model="gpt-5.6-luna",
        instructions=BASELINE_INSTRUCTIONS,
        input=report,
        text_format=IncidentAssessment,
    )

    return response.output_parsed


if __name__ == "__main__":
    test_report = (
        "Disabled tractor trailer blocking the right lane of "
        "I-4 eastbound near Exit 55."
    )

    assessment = assess_baseline(test_report)

    print("\n--- BASELINE ASSESSMENT ---")
    print(assessment.model_dump_json(indent=2))