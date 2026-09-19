from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.routes.auth import get_current_user
from app.db.session import get_db
from app.models.service import Service
from app.models.user import User
from app.schemas.service import ServiceCreate, ServiceRead
from app.services.access import enforce_usage_limit, record_usage

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[ServiceRead])
def list_services(db: Session = Depends(get_db)):
    return db.query(Service).order_by(Service.id).all()


@router.get("/{service_id}", response_model=ServiceRead)
def get_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    return service


@router.post("", response_model=ServiceRead, status_code=status.HTTP_201_CREATED)
def create_service(payload: ServiceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    enforce_usage_limit(db, current_user, "services")
    service = Service(**payload.model_dump())
    db.add(service)
    record_usage(db, current_user.id, "services")
    db.commit()
    db.refresh(service)
    return service
