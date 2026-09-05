import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from agent.report_parser import extract_reported_context
from schemas.models import ToolPlan, IncidentAssessment
from tools.traffic_tool import get_traffic_context
from tools.weather_tool import get_weather_context
from tools.sop_tool import get_sop_guidance
from tools.incident_details_tool import get_incident_details

load_dotenv(PROJECT_ROOT / ".env")

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


PLANNER_INSTRUCTIONS = """
You are the planning component of RoadOps AI, a roadway incident
decision-support proof of concept.

Your job is NOT to assess the final incident priority.

Your job is to determine what additional contextual information would
be useful for assessing the incident.

Available tools:

- Traffic Context Tool:
  Retrieves traffic level, queue status, current average speed,
  and normal speed.

- Weather Context Tool:
  Retrieves weather and visibility conditions.

- Incident Details Tool:
  Retrieves structured incident-management information such as
  incident type, blocked active lanes, roadway position/status,
  and incident duration.

- SOP Guidance Tool:
  Retrieves the RoadOps priority framework and relevant
  operating-procedure guidance.

Select only tools whose information could meaningfully improve
the assessment. 

Do not assume information that is not contained in the initial report.
"""


ASSESSOR_INSTRUCTIONS = """
You are the assessment component of RoadOps AI, a roadway incident
decision-support proof of concept.

You will receive:

1. The original incident report.
2. Context retrieved by RoadOps tools.
3. Relevant RoadOps POC policy guidance.

Use only the evidence provided.

Do not invent facts.

Priority must be one of:

LOW
MEDIUM
HIGH
CRITICAL
INSUFFICIENT_INFORMATION

Clearly identify the factors supporting the assessment.

If important information remains unavailable, include it in
missing_information.

Recommended actions must remain general decision-support suggestions.

RoadOps does not autonomously dispatch responders, control roadway
infrastructure, or make final operational decisions.

Missing information should reduce confidence or be reported under
missing_information, but it does not automatically require
INSUFFICIENT_INFORMATION.

Use INSUFFICIENT_INFORMATION only when the available evidence is not
strong enough to support a reasonable priority classification.

Strong observed operational impact, such as severe speed reduction,
heavy congestion, or a growing queue, may support a priority
classification even when another important field such as exact lane
position is unknown.

Do not invent the missing field. Base the classification on the
evidence that is actually available.
"""


def create_tool_plan(report: str) -> ToolPlan:
    response = client.responses.parse(
        model="gpt-5.6-luna",
        instructions=PLANNER_INSTRUCTIONS,
        input=report,
        text_format=ToolPlan,
    )

    return response.output_parsed


def assess_with_context(
    report: str,
    gathered_context: dict
) -> IncidentAssessment:

    assessment_input = f"""
INITIAL INCIDENT REPORT:
{report}

ROADOPS RETRIEVED CONTEXT:
{json.dumps(gathered_context, indent=2)}
"""

    response = client.responses.parse(
        model="gpt-5.6-luna",
        instructions=ASSESSOR_INSTRUCTIONS,
        input=assessment_input,
        text_format=IncidentAssessment,
    )

    return response.output_parsed


def run_roadops(incident_id: str, report: str):
    print("\n--- ROADOPS AGENT ---")

    # STEP 1: Determine which tools are needed.
    plan = create_tool_plan(report)

    print("\n[1] TOOL PLAN")
    print(plan.model_dump_json(indent=2))

    reported_context = extract_reported_context(report)
    gathered_context = {
    "reported_context": reported_context.model_dump()
    }

    # STEP 2: Call only the tools selected by the planner.

    if plan.use_traffic:
        print("\n[2] Calling Traffic Context Tool...")
        gathered_context["traffic"] = get_traffic_context(incident_id)

    if plan.use_weather:
        print("[3] Calling Weather Context Tool...")
        gathered_context["weather"] = get_weather_context(incident_id)

    if plan.use_incident_details:
        print("[4] Calling Incident Details Tool...")

        gathered_context["incident_details"] = (
            get_incident_details(incident_id)
        )

    if plan.use_sop:
        print("[5] Calling SOP Guidance Tool...")

        sop_query = (
            report
            + " incident priority classification "
            + "LOW MEDIUM HIGH CRITICAL "
        )

        if "traffic" in gathered_context:
            sop_query += " " + json.dumps(gathered_context["traffic"])

        if "weather" in gathered_context:
            sop_query += " " + json.dumps(gathered_context["weather"])

        if "incident_details" in gathered_context:
            sop_query += (
                " "
                + json.dumps(
                    gathered_context["incident_details"]
                )
            )
        sop_query += " " + json.dumps(
            gathered_context["reported_context"]
        )
        gathered_context["sop"] = get_sop_guidance(sop_query)

    print("\n[6] GATHERED CONTEXT")
    print(json.dumps(gathered_context, indent=2))

    # STEP 3: Perform the final assessment.
    assessment = assess_with_context(
        report,
        gathered_context
    )

    print("\n[7] ROADOPS ASSESSMENT")
    print(assessment.model_dump_json(indent=2))

    return {
        "tool_plan": plan,
        "context": gathered_context,
        "assessment": assessment
    }


if __name__ == "__main__":

    test_incident_id = "A4"

    test_report = (
        "Disabled vehicle reported on I-4 westbound near Exit 60. "
        
    )

    run_roadops(
        test_incident_id,
        test_report
    )