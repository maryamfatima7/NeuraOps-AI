import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.ai.gemini_service import GeminiService
from app.db.session import get_db
from app.api.routes.auth import get_current_user
from app.models.ai_analysis import AIAnalysis
from app.models.anomaly import Anomaly
from app.models.incident import Incident
from app.models.log import LogEntry
from app.models.service import Service
from app.schemas.incident import AIAnalysisRequest, AIAnalysisOut, IncidentCreate, IncidentRead, IncidentStatusUpdate
from app.models.user import User
from app.services.access import enforce_usage_limit, record_usage

router = APIRouter(dependencies=[Depends(get_current_user)])


def serialize_incident(incident: Incident) -> dict:
    affected_services = incident.affected_services
    if isinstance(affected_services, str):
        try:
            parsed = json.loads(affected_services)
            if isinstance(parsed, list):
                affected_services = parsed
            else:
                affected_services = [part.strip() for part in affected_services.split(',') if part.strip()]
        except json.JSONDecodeError:
            affected_services = [part.strip() for part in affected_services.split(',') if part.strip()]

    return {
        "id": incident.id,
        "title": incident.title,
        "description": incident.description,
        "severity": incident.severity,
        "status": incident.status,
        "affected_services": affected_services,
        "detected_time": incident.detected_time,
        "updated_time": incident.updated_time,
        "anomaly_references": incident.anomaly_references,
        "related_logs": incident.related_logs,
        "root_cause": incident.root_cause,
        "ai_analysis": incident.ai_analysis,
        "recommendations": incident.recommendations,
        "service_id": incident.service_id,
    }


@router.get("")
def list_incidents(db: Session = Depends(get_db)):
    incidents = db.query(Incident).order_by(Incident.detected_time.desc()).all()
    return [serialize_incident(incident) for incident in incidents]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_incident(payload: IncidentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    enforce_usage_limit(db, current_user, "incidents")
    service_names = json.dumps(payload.affected_services)
    incident = Incident(
        title=payload.title,
        description=payload.description,
        severity=payload.severity,
        status=payload.status,
        affected_services=service_names,
        anomaly_references=str(payload.anomaly_references) if payload.anomaly_references else None,
        related_logs=str(payload.related_logs) if payload.related_logs else None,
        root_cause=payload.root_cause,
        ai_analysis=payload.ai_analysis,
        recommendations=payload.recommendations,
        detected_time=datetime.utcnow(),
        updated_time=datetime.utcnow(),
    )
    db.add(incident)
    record_usage(db, current_user.id, "incidents")
    db.commit()
    db.refresh(incident)
    return serialize_incident(incident)


@router.get("/{incident_id}", response_model=dict)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    anomalies = db.query(Anomaly).filter(Anomaly.service_id.in_([svc.id for svc in db.query(Service).all() if svc.name in incident.affected_services.split(', ')])).all()
    logs = db.query(LogEntry).order_by(LogEntry.timestamp.desc()).limit(20).all()
    ai = db.query(AIAnalysis).filter(AIAnalysis.incident_id == incident.id).order_by(AIAnalysis.created_at.desc()).first()
    return {
        "id": incident.id,
        "title": incident.title,
        "description": incident.description,
        "severity": incident.severity,
        "status": incident.status,
        "affected_services": incident.affected_services.split(', ') if incident.affected_services else [],
        "detected_time": incident.detected_time.isoformat(),
        "updated_time": incident.updated_time.isoformat(),
        "root_cause": incident.root_cause,
        "ai_analysis": incident.ai_analysis,
        "recommendations": incident.recommendations,
        "related_logs": logs[:10],
        "anomalies": [{
            "metric": x.metric,
            "observed_value": x.observed_value,
            "expected_baseline": x.expected_baseline,
            "deviation": x.deviation,
            "severity": x.severity,
            "explanation": x.explanation,
            "timestamp": x.timestamp.isoformat(),
        } for x in anomalies],
        "ai_summary": ai.summary if ai else None,
    }


@router.patch("/{incident_id}/status", response_model=dict)
def update_incident_status(incident_id: int, payload: IncidentStatusUpdate, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    incident.status = payload.status
    incident.updated_time = datetime.utcnow()
    db.commit()
    db.refresh(incident)
    return serialize_incident(incident)


@router.post("/{incident_id}/ai-analysis", response_model=AIAnalysisOut)
async def trigger_ai_analysis(incident_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    enforce_usage_limit(db, current_user, "ai_analyses")
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")

    related_logs = db.query(LogEntry).order_by(LogEntry.timestamp.desc()).limit(15).all()
    anomalies = db.query(Anomaly).order_by(Anomaly.timestamp.desc()).limit(10).all()
    service_names = [name.strip() for name in incident.affected_services.split(', ') if name.strip()]
    incident_context = {
        "incident_id": incident.id,
        "incident_title": incident.title,
        "description": incident.description,
        "severity": incident.severity,
        "affected_services": service_names,
        "logs": [f"{log.level}: {log.message}" for log in related_logs],
        "anomalies": [f"{anomaly.metric}={anomaly.observed_value} expected {anomaly.expected_baseline}" for anomaly in anomalies],
        "metrics": ["latency spike", "error rate increase"],
        "events": [incident.description],
    }

    result = await GeminiService().analyze_incident(incident_context)
    ai_record = AIAnalysis(
        incident_id=incident.id,
        summary=result["summary"],
        suspected_root_cause=result["suspected_root_cause"],
        confidence=result["confidence"],
        evidence="\n".join(result["evidence"]),
        affected_components=", ".join(result["affected_components"]),
        recommended_actions="\n".join(result["recommended_actions"]),
        investigation_steps="\n".join(result["investigation_steps"]),
    )
    db.add(ai_record)
    record_usage(db, current_user.id, "ai_analyses")
    incident.ai_analysis = result["summary"]
    incident.root_cause = result["suspected_root_cause"]
    incident.recommendations = "\n".join(result["recommended_actions"])
    db.commit()

    return AIAnalysisOut(
        summary=result["summary"],
        suspected_root_cause=result["suspected_root_cause"],
        confidence=result["confidence"],
        evidence=result["evidence"],
        affected_components=result["affected_components"],
        recommended_actions=result["recommended_actions"],
        investigation_steps=result["investigation_steps"],
    )
