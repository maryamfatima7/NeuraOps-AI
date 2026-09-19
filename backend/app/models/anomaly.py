from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.service import Service


class Anomaly(Base):
    __tablename__ = "anomalies"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    service_id: Mapped[int | None] = mapped_column(ForeignKey("services.id"), index=True, nullable=True)
    metric: Mapped[str] = mapped_column(String(60), index=True)
    observed_value: Mapped[float] = mapped_column(Float)
    expected_baseline: Mapped[float] = mapped_column(Float)
    deviation: Mapped[float] = mapped_column(Float)
    severity: Mapped[str] = mapped_column(String(20), index=True)
    explanation: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    service: Mapped["Service"] = relationship(back_populates="anomalies")
