from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class ReportedContext(BaseModel):
    roadway: Optional[str] = None
    direction: Optional[str] = None

    incident_type: Optional[str] = None

    lane_impact: Optional[str] = None
    blocked_active_lanes: Optional[int] = None

    traffic_level: Optional[str] = None
    queue_status: Optional[str] = None

    weather: Optional[str] = None
    visibility: Optional[str] = None

    duration_minutes: Optional[int] = None


class IncidentInput(BaseModel):
    incident_id: str
    report: str


class IncidentContext(BaseModel):
    traffic_level: Optional[str] = None
    queue_status: Optional[str] = None
    average_speed_mph: Optional[float] = None
    normal_speed_mph: Optional[float] = None
    weather: Optional[str] = None
    visibility: Optional[str] = None

class ToolPlan(BaseModel):
    use_traffic: bool
    use_weather: bool
    use_incident_details: bool
    use_sop: bool

    traffic_reason: Optional[str] = None
    weather_reason: Optional[str] = None
    incident_details_reason: Optional[str] = None
    sop_reason: Optional[str] = None

class IncidentAssessment(BaseModel):
    priority: Literal[
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
        "INSUFFICIENT_INFORMATION"
    ]

    confidence: float = Field(ge=0.0, le=1.0)

    identified_factors: List[str]
    recommended_actions: List[str]
    missing_information: List[str]

    reasoning_summary: str