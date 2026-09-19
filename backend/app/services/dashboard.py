from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.anomaly import Anomaly
from app.models.incident import Incident
from app.models.log import LogEntry
from app.models.metric import Metric
from app.models.service import Service


def get_dashboard_summary(db: Session):
    services = db.query(Service).all()
    incidents = db.query(Incident).order_by(Incident.detected_time.desc()).limit(5).all()
    anomalies = db.query(Anomaly).order_by(Anomaly.timestamp.desc()).limit(10).all()
    alerts = db.query(Alert).order_by(Alert.created_at.desc()).limit(8).all()
    logs = db.query(LogEntry).order_by(LogEntry.timestamp.desc()).limit(10).all()
    active_incidents = db.query(Incident).filter(Incident.status != "RESOLVED").count()
    avg_latency = round(sum(service.latency_ms for service in services) / len(services), 2) if services else 0
    error_rate = round(sum(service.error_rate for service in services) / len(services), 2) if services else 0
    req_per_min = round(sum(service.request_rate for service in services), 2) if services else 0
    return {
        "overall_health": "healthy" if active_incidents < 3 else "degraded",
        "active_incidents": active_incidents,
        "error_rate": error_rate,
        "average_latency": avg_latency,
        "requests_per_minute": req_per_min,
        "services_monitored": len(services),
        "recent_alerts": [
            {
                "rule": alert.rule,
                "service": alert.service.name if alert.service else "unknown",
                "severity": alert.severity,
                "status": alert.status,
                "created_at": alert.created_at.isoformat(),
            }
            for alert in alerts
        ],
        "recent_incidents": [
            {
                "id": incident.id,
                "title": incident.title,
                "severity": incident.severity,
                "status": incident.status,
                "detected_time": incident.detected_time.isoformat(),
            }
            for incident in incidents
        ],
        "ai_detected_anomalies": [
            {
                "metric": anomaly.metric,
                "service": anomaly.service.name if anomaly.service else "unknown",
                "severity": anomaly.severity,
                "deviation": anomaly.deviation,
                "timestamp": anomaly.timestamp.isoformat(),
            }
            for anomaly in anomalies
        ],
        "logs": [
            {
                "service": log.service.name if log.service else "unknown",
                "level": log.level,
                "message": log.message,
                "timestamp": log.timestamp.isoformat(),
            }
            for log in logs
        ],
    }
