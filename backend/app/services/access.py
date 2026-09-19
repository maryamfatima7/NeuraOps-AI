from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.usage import UsageRecord
from app.models.user import User


def get_plan_limits(plan: str) -> dict[str, int | bool]:
    settings = get_settings()
    return settings.free_plan_limits if plan == "FREE" else settings.pro_plan_limits


def feature_is_allowed(plan: str, feature: str) -> bool:
    settings = get_settings()
    access = settings.feature_access_matrix.get(feature, {})
    return bool(access.get(plan, False))


def require_plan(user: User, feature: str, *, message: str | None = None) -> None:
    if user.plan == "PRO":
        return
    if feature_is_allowed(user.plan, feature):
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "code": "PLAN_REQUIRED",
            "message": message or "This feature requires the PRO plan.",
            "required_plan": "PRO",
            "current_plan": user.plan,
        },
    )


def _usage_key_to_limit_key(metric: str) -> str:
    mapping = {
        "services": "max_services",
        "logs": "max_logs_per_day",
        "incidents": "max_incidents_per_day",
        "ai_analyses": "max_ai_analyses_per_day",
    }
    return mapping.get(metric, metric)


def get_usage_count(db: Session, user_id: int, metric: str, start: datetime, end: datetime) -> int:
    record = (
        db.query(func.coalesce(func.sum(UsageRecord.value), 0))
        .filter(
            UsageRecord.user_id == user_id,
            UsageRecord.metric == metric,
            UsageRecord.period_start < end,
            UsageRecord.period_end > start,
        )
        .scalar()
    )
    return int(record or 0)


def record_usage(db: Session, user_id: int, metric: str, *, amount: int = 1) -> None:
    period_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    period_end = period_start + timedelta(days=1)
    record = (
        db.query(UsageRecord)
        .filter(
            UsageRecord.user_id == user_id,
            UsageRecord.metric == metric,
            UsageRecord.period_start == period_start,
            UsageRecord.period_end == period_end,
        )
        .first()
    )
    if record:
        record.value += amount
    else:
        db.add(UsageRecord(user_id=user_id, metric=metric, value=amount, period_start=period_start, period_end=period_end))
    db.flush()


def enforce_usage_limit(db: Session, user: User, metric: str, *, amount: int = 1) -> None:
    if user.plan == "PRO":
        return

    settings = get_settings()
    limits = settings.free_plan_limits
    limit_key = _usage_key_to_limit_key(metric)
    limit_value = limits.get(limit_key, -1)
    if limit_value in (None, -1):
        return

    now = datetime.utcnow()
    current_usage = get_usage_count(db, user.id, metric, now.replace(hour=0, minute=0, second=0, microsecond=0), now)
    if current_usage + amount > int(limit_value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "USAGE_LIMIT_EXCEEDED",
                "message": f"{metric.replace('_', ' ').title()} quota reached for the FREE plan.",
                "current_plan": user.plan,
                "limit": limit_value,
                "used": current_usage,
                "remaining": max(int(limit_value) - current_usage, 0),
            },
        )
