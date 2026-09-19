from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.telemetry import router as telemetry_router
from app.api.routes.services import router as services_router
from app.api.routes.incidents import router as incidents_router
from app.api.routes.logs import router as logs_router
from app.api.routes.metrics import router as metrics_router
from app.api.routes.alerts import router as alerts_router
from app.api.routes.ai import router as ai_router
from app.api.routes.dashboard import router as dashboard_router

router = APIRouter()
api_router = router

router.include_router(health_router, prefix="/health", tags=["Health"])
router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(telemetry_router, prefix="/telemetry", tags=["Telemetry"])
router.include_router(services_router, prefix="/services", tags=["Services"])
router.include_router(incidents_router, prefix="/incidents", tags=["Incidents"])
router.include_router(logs_router, prefix="/logs", tags=["Logs"])
router.include_router(metrics_router, prefix="/metrics", tags=["Metrics"])
router.include_router(alerts_router, prefix="/alerts", tags=["Alerts"])
router.include_router(ai_router, prefix="/ai", tags=["AI Analysis"])
router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
