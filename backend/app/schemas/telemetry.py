from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class LogEventCreate(BaseModel):
    service: str
    level: str = Field(..., pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    message: str
    metadata: dict[str, Any] | None = None
    correlation_id: str | None = None
    timestamp: datetime | None = None


class MetricEventCreate(BaseModel):
    service: str
    metric_name: str
    value: float
    unit: str | None = None
    timestamp: datetime | None = None


class ServiceHealthEventCreate(BaseModel):
    service: str
    status: str
    uptime: float | None = None
    latency_ms: float | None = None
    request_rate: float | None = None
    timestamp: datetime | None = None


class ErrorEventCreate(BaseModel):
    service: str
    message: str
    error_type: str | None = None
    stacktrace: str | None = None
    timestamp: datetime | None = None


class HTTPRequestEventCreate(BaseModel):
    service: str
    method: str
    path: str
    status_code: int = Field(..., ge=100, le=599)
    latency_ms: float
    request_id: str | None = None
    timestamp: datetime | None = None


class TelemetryEventCreate(BaseModel):
    event_type: str
    service: str
    summary: str
    payload: dict[str, Any] | None = None
    timestamp: datetime | None = None
