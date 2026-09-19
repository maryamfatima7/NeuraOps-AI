from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import TokenResponse, UserRegister, UserResponse
from app.services.access import feature_is_allowed, get_plan_limits, get_usage_count

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    from app.core.security import decode_access_token

    user_id = decode_access_token(token)
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found for this token")
    return user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    if payload.confirm_password is not None and payload.password != payload.confirm_password:
        raise HTTPException(status_code=400, detail={"code": "PASSWORD_MISMATCH", "message": "Passwords do not match"})

    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail={"code": "EMAIL_ALREADY_EXISTS", "message": "A user with this email already exists"})

    if len(payload.password) < 8:
        raise HTTPException(status_code=400, detail={"code": "WEAK_PASSWORD", "message": "Password must be at least 8 characters long"})

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        plan="FREE",
        plan_status="ACTIVE",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"code": "INVALID_CREDENTIALS", "message": "Incorrect email or password"})

    settings = get_settings()
    access_token = create_access_token(
        subject=str(user.id),
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/usage")
def usage(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from datetime import timedelta

    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    usage = {
        "services": get_usage_count(db, current_user.id, "services", today, tomorrow),
        "logs": get_usage_count(db, current_user.id, "logs", today, tomorrow),
        "incidents": get_usage_count(db, current_user.id, "incidents", today, tomorrow),
        "ai_analyses": get_usage_count(db, current_user.id, "ai_analyses", today, tomorrow),
    }
    limits = get_plan_limits(current_user.plan)
    remaining = {
        "max_services": -1 if limits.get("max_services") == -1 else max(int(limits.get("max_services", 0)) - usage["services"], 0),
        "max_logs_per_day": -1 if limits.get("max_logs_per_day") == -1 else max(int(limits.get("max_logs_per_day", 0)) - usage["logs"], 0),
        "max_incidents_per_day": -1 if limits.get("max_incidents_per_day") == -1 else max(int(limits.get("max_incidents_per_day", 0)) - usage["incidents"], 0),
        "max_ai_analyses_per_day": -1 if limits.get("max_ai_analyses_per_day") == -1 else max(int(limits.get("max_ai_analyses_per_day", 0)) - usage["ai_analyses"], 0),
    }
    return {
        "plan": current_user.plan,
        "plan_status": current_user.plan_status,
        "usage": usage,
        "limits": limits,
        "remaining": remaining,
        "features": {name: feature_is_allowed(current_user.plan, name) for name in get_settings().feature_access_matrix},
    }
