from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.log import LogEntry
    from app.models.metric import Metric
    from app.models.alert import Alert
    from app.models.incident import Incident
    from app.models.anomaly import Anomaly


class Service(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(40), default="healthy")
    uptime: Mapped[float] = mapped_column(Float, default=99.9)
    request_rate: Mapped[float] = mapped_column(Float, default=0.0)
    error_rate: Mapped[float] = mapped_column(Float, default=0.0)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    dependencies: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    logs: Mapped[list["LogEntry"]] = relationship(back_populates="service")
    metrics: Mapped[list["Metric"]] = relationship(back_populates="service")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="service")
    incidents: Mapped[list["Incident"]] = relationship(back_populates="service")
    anomalies: Mapped[list["Anomaly"]] = relationship(back_populates="service")
