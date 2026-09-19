from datetime import datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.routes.auth import get_current_user
from app.models.alert import Alert
from app.models.service import Service
from app.schemas.alert import AlertCreate, AlertRead

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[AlertRead])
def list_alerts(db: Session = Depends(get_db)):
    return db.query(Alert).order_by(Alert.created_at.desc()).all()


@router.post("", response_model=AlertRead, status_code=status.HTTP_201_CREATED)
def create_alert(payload: AlertCreate, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.name == payload.service).first()
    alert = Alert(
        service_id=service.id if service else None,
        rule=payload.rule,
        threshold=payload.threshold,
        current_value=payload.current_value,
        severity=payload.severity,
        status=payload.status,
        created_at=datetime.utcnow(),
        description=payload.description,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert
