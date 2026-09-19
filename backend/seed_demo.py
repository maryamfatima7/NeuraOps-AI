import json
from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.db.base import Base
from app.models.ai_analysis import AIAnalysis
from app.models.alert import Alert
from app.models.anomaly import Anomaly
from app.models.incident import Incident
from app.models.log import LogEntry
from app.models.metric import Metric
from app.models.service import Service
from app.models.telemetry_event import TelemetryEvent

settings = get_settings()
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

SERVICE_NAMES = [
    "API Gateway",
    "Authentication Service",
    "User Service",
    "Payment Service",
    "AI Inference Service",
    "PostgreSQL",
    "Notification Service",
]


def reset_demo_data():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    services = []
    for idx, name in enumerate(SERVICE_NAMES):
        service = Service(
            name=name,
            status="healthy" if idx < 5 else "degraded",
            uptime=99.5 + idx * 0.1,
            request_rate=180 + idx * 35,
            error_rate=0.2 + idx * 0.08,
            latency_ms=80 + idx * 20,
            description=f"Operational service for {name}.",
            dependencies="PostgreSQL" if idx == 3 else "API Gateway" if idx > 0 else "External Router",
            owner="Platform Team",
        )
        services.append(service)
        db.add(service)
    db.commit()

    for service in services:
        now = datetime.utcnow()
        db.add(LogEntry(
            service_id=service.id,
            level="ERROR" if service.name in {"Payment Service", "PostgreSQL"} else "INFO",
            message=(
                "HTTP 504 from PostgreSQL after connection pool timeout."
                if service.name == "Payment Service"
                else "Database timeout while acquiring a PostgreSQL connection."
                if service.name == "PostgreSQL"
                else "Request processed successfully."
            ),
            details=json.dumps({"region": "us-east-1", "pod": f"pod-{service.id}"}),
            correlation_id=f"corr-{service.id}",
            timestamp=now - timedelta(minutes=service.id),
        ))
        db.add(Metric(
            service_id=service.id,
            metric_name="latency_ms",
            value=service.latency_ms + (470 if service.name == "Payment Service" else 15 if service.name == "PostgreSQL" else 0),
            unit="ms",
            timestamp=now - timedelta(minutes=service.id),
        ))
        db.add(TelemetryEvent(
            service_id=service.id,
            event_type="http_request",
            summary=(
                f"POST /payments returned HTTP 503 at {service.request_rate} rpm."
                if service.name == "Payment Service"
                else f"{service.name} processed requests at {service.request_rate} rpm."
            ),
            payload=json.dumps({"requests": service.request_rate, "status_code": 503 if service.name == "Payment Service" else 200}),
            timestamp=now - timedelta(minutes=service.id),
        ))

    db.add(Anomaly(
        service_id=1,
        metric="latency_ms",
        observed_value=780.5,
        expected_baseline=310.0,
        deviation=470.5,
        severity="HIGH",
        explanation="Latency deviated from recent baseline due to database timeout cascade.",
        timestamp=datetime.utcnow() - timedelta(minutes=12),
    ))

    incident = Incident(
        service_id=1,
        title="Payment Service Elevated Latency",
        description="Payment requests slowed sharply as PostgreSQL connection timeouts and HTTP 5xx responses increased under elevated traffic.",
        severity="CRITICAL",
        status="INVESTIGATING",
        affected_services="Payment Service, API Gateway, PostgreSQL",
        anomaly_references='["latency_ms:780.5"]',
        related_logs='["ERROR: PostgreSQL connection timeout", "ERROR: payment request returned HTTP 503", "WARNING: connection pool saturation"]',
        root_cause=None,
        ai_analysis=None,
        recommendations=None,
        detected_time=datetime.utcnow() - timedelta(minutes=10),
        updated_time=datetime.utcnow() - timedelta(minutes=3),
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)

    db.add(AIAnalysis(
        incident_id=incident.id,
        summary="Observed latency and timeout patterns indicate a dependency bottleneck in the database layer, with elevated request pressure likely amplifying the issue.",
        suspected_root_cause="Database connection saturation and likely timeout behavior are the probable root cause, but verification is required against the specific query and config changes.",
        confidence=0.86,
        evidence="Database timeout pattern, latency spike, API gateway saturation",
        affected_components="API Gateway, Database, Payment Service",
        recommended_actions="Scale database connections, inspect slow query logs, reduce retry pressure during peak traffic",
        investigation_steps="Confirm slow query logs, verify connection pool limits, check recent deployment impact",
        created_at=datetime.utcnow(),
    ))

    db.add(Alert(
        service_id=1,
        rule="latency > threshold",
        threshold=500,
        current_value=780.5,
        severity="CRITICAL",
        status="open",
        created_at=datetime.utcnow(),
        description="API Gateway latency exceeded the threshold.",
    ))

    db.commit()
    db.close()
    print("Demo data seeded successfully")


if __name__ == "__main__":
    reset_demo_data()
