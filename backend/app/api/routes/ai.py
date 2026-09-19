from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.ai.gemini_service import GeminiService
from app.api.routes.auth import get_current_user
from app.db.session import get_db
from app.models.incident import Incident
from app.models.user import User
from app.schemas.incident import AIAnalysisOut, AIAnalysisRequest
from app.services.access import require_plan

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post("/analyze", response_model=AIAnalysisOut)
async def analyze_incident(payload: AIAnalysisRequest, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == payload.incident_id).first()
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")

    context = {
        "incident_id": incident.id,
        "incident_title": payload.incident_title,
        "description": payload.description,
        "severity": payload.severity,
        "affected_services": payload.affected_services,
        "logs": payload.logs,
        "anomalies": payload.anomalies,
        "metrics": payload.metrics,
        "events": payload.events,
    }
    result = await GeminiService().analyze_incident(context)
    return AIAnalysisOut(
        summary=result["summary"],
        suspected_root_cause=result["suspected_root_cause"],
        confidence=result["confidence"],
        evidence=result["evidence"],
        affected_components=result["affected_components"],
        recommended_actions=result["recommended_actions"],
        investigation_steps=result["investigation_steps"],
    )


@router.post("/pro-analysis", response_model=AIAnalysisOut)
async def pro_analysis(
    payload: AIAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_plan(current_user, "advanced_ai_rca", message="Advanced AI root-cause analysis requires the PRO plan.")
    return await analyze_incident(payload, db)
