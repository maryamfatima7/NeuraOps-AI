from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class IncidentBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=180)
    description: str
    severity: str = Field(..., pattern=r"^(LOW|MEDIUM|HIGH|CRITICAL)$")
    status: str = Field(default="OPEN", pattern=r"^(OPEN|INVESTIGATING|MITIGATED|RESOLVED)$")
    affected_services: list[str] = []
    anomaly_references: list[str] | None = None
    related_logs: list[str] | None = None
    root_cause: str | None = None
    ai_analysis: str | None = None
    recommendations: str | None = None


class IncidentCreate(IncidentBase):
    pass


class IncidentStatusUpdate(BaseModel):
    status: str = Field(..., pattern=r"^(OPEN|INVESTIGATING|MITIGATED|RESOLVED)$")


class IncidentRead(IncidentBase):
    id: int
    detected_time: datetime
    updated_time: datetime
    service_id: int | None = None

    class Config:
        from_attributes = True


class AIAnalysisOut(BaseModel):
    summary: str
    suspected_root_cause: str
    confidence: float
    evidence: list[str]
    affected_components: list[str]
    recommended_actions: list[str]
    investigation_steps: list[str]


class AIAnalysisRequest(BaseModel):
    incident_id: int
    incident_title: str
    description: str
    severity: str
    affected_services: list[str]
    logs: list[str] = []
    anomalies: list[str] = []
    metrics: list[str] = []
    events: list[str] = []
