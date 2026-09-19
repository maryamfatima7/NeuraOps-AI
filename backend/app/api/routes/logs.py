from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.routes.auth import get_current_user
from app.models.log import LogEntry
from app.models.service import Service

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[dict])
def list_logs(
    service: str | None = Query(default=None),
    level: str | None = Query(default=None),
    limit: int = Query(default=100, le=300),
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
):
    query = db.query(LogEntry)
    if service:
        service_obj = db.query(Service).filter(Service.name == service).first()
        if service_obj:
            query = query.filter(LogEntry.service_id == service_obj.id)
    if level:
        query = query.filter(LogEntry.level == level.upper())
    logs = query.order_by(LogEntry.timestamp.desc()).offset((page - 1) * limit).limit(limit).all()
    return [{
        "id": log.id,
        "service": log.service.name if log.service else "unknown",
        "level": log.level,
        "message": log.message,
        "metadata": log.details,
        "correlation_id": log.correlation_id,
        "timestamp": log.timestamp.isoformat(),
    } for log in logs]


@router.get("/{log_id}", response_model=dict)
def get_log(log_id: int, db: Session = Depends(get_db)):
    log = db.query(LogEntry).filter(LogEntry.id == log_id).first()
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")
    return {
        "id": log.id,
        "service": log.service.name if log.service else "unknown",
        "level": log.level,
        "message": log.message,
        "metadata": log.details,
        "correlation_id": log.correlation_id,
        "timestamp": log.timestamp.isoformat(),
    }
