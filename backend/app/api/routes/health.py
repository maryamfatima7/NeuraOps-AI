from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db

router = APIRouter()


@router.get("", summary="API health")
def read_health(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        db_status = "ok"
    except Exception:
        db_status = "degraded"
    return {
        "status": "ok",
        "database": db_status,
        "redis": "ok",
        "telemetry": "ok",
        "ai_service": "degraded",
    }
