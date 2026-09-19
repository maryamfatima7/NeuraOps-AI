from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.service import Service


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    service_id: Mapped[int | None] = mapped_column(ForeignKey("services.id"), index=True, nullable=True)
    rule: Mapped[str] = mapped_column(String(120), index=True)
    threshold: Mapped[float] = mapped_column(Float)
    current_value: Mapped[float] = mapped_column(Float)
    severity: Mapped[str] = mapped_column(String(20), index=True)
    status: Mapped[str] = mapped_column(String(20), default="open", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    service: Mapped["Service"] = relationship(back_populates="alerts")
