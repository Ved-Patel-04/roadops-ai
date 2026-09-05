import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from schemas.models import ReportedContext


PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

MODEL = "gpt-5.6-luna"


def extract_reported_context(report: str) -> ReportedContext:
    response = client.responses.parse(
        model=MODEL,
        input=[
            {
                "role": "system",
                "content": """
You extract structured roadway-incident facts from an operator's
initial report.

Only extract facts that are explicitly stated.

Do not infer missing facts.

Examples:
- "heavy rain" -> weather = "heavy rain"
- Do NOT automatically set visibility = "reduced" unless reduced
  visibility is explicitly stated.
- "right lane blocked" -> lane_impact = "right lane blocked"
- If exactly one active lane is explicitly described as blocked,
  blocked_active_lanes may be 1.
- If traffic conditions are not stated, leave traffic_level null.
- If duration is not stated, leave duration_minutes null.

Return null for anything not directly supported by the report.
""",
            },
            {
                "role": "user",
                "content": report,
            },
        ],
        text_format=ReportedContext,
    )

    return response.output_parsed
