from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.routes.auth import get_current_user
from app.models.metric import Metric
from app.models.service import Service
from app.schemas.telemetry import MetricEventCreate

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[dict])
def list_metrics(
    service: str | None = Query(default=None),
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(Metric)
    if service:
        service_obj = db.query(Service).filter(Service.name == service).first()
        if service_obj:
            query = query.filter(Metric.service_id == service_obj.id)
    metrics = query.order_by(Metric.timestamp.desc()).limit(limit).all()
    return [{
        "service": metric.service.name if metric.service else "unknown",
        "metric_name": metric.metric_name,
        "value": metric.value,
        "unit": metric.unit,
        "timestamp": metric.timestamp.isoformat(),
    } for metric in metrics]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_metric(payload: MetricEventCreate, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.name == payload.service).first()
    if service is None:
        service = Service(name=payload.service, status="healthy")
        db.add(service)
        db.commit()
        db.refresh(service)
    metric = Metric(
        service_id=service.id,
        metric_name=payload.metric_name,
        value=payload.value,
        unit=payload.unit,
        timestamp=payload.timestamp or __import__('datetime').datetime.utcnow(),
    )
    db.add(metric)
    db.commit()
    return {"status": "created"}
