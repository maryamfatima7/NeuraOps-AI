from datetime import datetime

from pydantic import BaseModel, Field


class AlertCreate(BaseModel):
    rule: str
    service: str
    threshold: float
    current_value: float
    severity: str = Field(..., pattern=r"^(LOW|MEDIUM|HIGH|CRITICAL)$")
    status: str = Field(default="open", pattern=r"^(open|acknowledged|resolved)$")
    description: str | None = None


class AlertRead(AlertCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
