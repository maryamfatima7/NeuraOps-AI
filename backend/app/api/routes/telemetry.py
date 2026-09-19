from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.routes.auth import get_current_user
from app.detection.baseline import BaselineDetector
from app.models.anomaly import Anomaly
from app.models.log import LogEntry
from app.models.metric import Metric
from app.models.service import Service
from app.models.telemetry_event import TelemetryEvent
from app.schemas.telemetry import (
    ErrorEventCreate,
    HTTPRequestEventCreate,
    LogEventCreate,
    MetricEventCreate,
    ServiceHealthEventCreate,
    TelemetryEventCreate,
)
from app.models.user import User
from app.services.access import enforce_usage_limit, record_usage

router = APIRouter(dependencies=[Depends(get_current_user)])
detector = BaselineDetector()


def ensure_service(db: Session, name: str) -> Service:
    service = db.query(Service).filter(Service.name == name).first()
    if service:
        return service
    service = Service(name=name, status="healthy")
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


@router.post("/logs", status_code=status.HTTP_201_CREATED)
def ingest_logs(payload: LogEventCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    enforce_usage_limit(db, current_user, "logs")
    service = ensure_service(db, payload.service)
    log = LogEntry(
        service_id=service.id,
        level=payload.level,
        message=payload.message,
        details=str(payload.metadata) if payload.metadata else None,
        correlation_id=payload.correlation_id,
        timestamp=payload.timestamp or datetime.utcnow(),
    )
    db.add(log)
    record_usage(db, current_user.id, "logs")
    db.commit()
    return {"status": "created", "service": service.name}


@router.post("/metrics", status_code=status.HTTP_201_CREATED)
def ingest_metrics(payload: MetricEventCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = ensure_service(db, payload.service)
    metric = Metric(
        service_id=service.id,
        metric_name=payload.metric_name,
        value=payload.value,
        unit=payload.unit,
        timestamp=payload.timestamp or datetime.utcnow(),
    )
    db.add(metric)
    db.commit()

    detector.update(payload.service, payload.metric_name, payload.value)
    anomaly = detector.analyze(payload.service, payload.metric_name, payload.value)
    if anomaly:
        db_anomaly = Anomaly(
            service_id=service.id,
            metric=anomaly["metric"],
            observed_value=anomaly["observed_value"],
            expected_baseline=anomaly["expected_baseline"],
            deviation=anomaly["deviation"],
            severity=anomaly["severity"],
            explanation=anomaly["explanation"],
            timestamp=anomaly["timestamp"],
        )
        db.add(db_anomaly)
        db.commit()
    return {"status": "created", "anomaly_detected": anomaly is not None}


@router.post("/events", status_code=status.HTTP_201_CREATED)
def ingest_event(payload: TelemetryEventCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = ensure_service(db, payload.service)
    event = TelemetryEvent(
        service_id=service.id,
        event_type=payload.event_type,
        summary=payload.summary,
        payload=str(payload.payload) if payload.payload else None,
        timestamp=payload.timestamp or datetime.utcnow(),
    )
    db.add(event)
    db.commit()
    return {"status": "created"}


@router.post("/errors", status_code=status.HTTP_201_CREATED)
def ingest_error(payload: ErrorEventCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    enforce_usage_limit(db, current_user, "logs")
    service = ensure_service(db, payload.service)
    log = LogEntry(
        service_id=service.id,
        level="ERROR",
        message=payload.message,
        details=f"{payload.error_type}::{payload.stacktrace or ''}",
        timestamp=payload.timestamp or datetime.utcnow(),
    )
    db.add(log)
    record_usage(db, current_user.id, "logs")
    db.commit()
    return {"status": "created"}


@router.post("/http-requests", status_code=status.HTTP_201_CREATED)
def ingest_http_request(payload: HTTPRequestEventCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = ensure_service(db, payload.service)
    event = TelemetryEvent(
        service_id=service.id,
        event_type="http_request",
        summary=f"{payload.method} {payload.path} -> {payload.status_code}",
        payload=f"latency_ms={payload.latency_ms};request_id={payload.request_id};status_code={payload.status_code}",
        timestamp=payload.timestamp or datetime.utcnow(),
    )
    db.add(event)
    db.commit()
    return {"status": "created"}


@router.post("/health", status_code=status.HTTP_201_CREATED)
def ingest_health(payload: ServiceHealthEventCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = ensure_service(db, payload.service)
    service.status = payload.status
    service.uptime = payload.uptime if payload.uptime is not None else service.uptime
    service.latency_ms = payload.latency_ms if payload.latency_ms is not None else service.latency_ms
    service.request_rate = payload.request_rate if payload.request_rate is not None else service.request_rate
    db.add(service)
    db.commit()
    return {"status": "updated"}


@router.get("", response_model=list[dict])
def list_telemetry(
    service: str | None = Query(default=None),
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(TelemetryEvent)
    if service:
        service_id = db.query(Service.id).filter(Service.name == service).scalar()
        if service_id:
            query = query.filter(TelemetryEvent.service_id == service_id)
    results = query.order_by(TelemetryEvent.timestamp.desc()).limit(limit).all()
    return [{
        "event_type": event.event_type,
        "service": event.service.name if event.service else "unknown",
        "summary": event.summary,
        "timestamp": event.timestamp.isoformat(),
    } for event in results]
