from pydantic import BaseModel, Field


class ServiceBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    status: str = "healthy"
    uptime: float = 99.9
    request_rate: float = 0.0
    error_rate: float = 0.0
    latency_ms: float = 0.0
    description: str | None = None
    dependencies: str | None = None
    owner: str | None = None


class ServiceCreate(ServiceBase):
    pass


class ServiceRead(ServiceBase):
    id: int

    class Config:
        from_attributes = True
