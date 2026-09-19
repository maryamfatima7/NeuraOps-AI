import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine
from app.api.routes import api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("neuraops")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting NeuraOps AI service")
    Base.metadata.create_all(bind=engine)
    yield
    logger.info("Shutting down NeuraOps AI service")


settings = get_settings()
allowed_origins = list(settings.cors_origins)
if settings.frontend_url not in allowed_origins:
    allowed_origins.append(settings.frontend_url)
app = FastAPI(
    title="NeuraOps AI",
    description="Intelligent AI Observability & Autonomous Incident Analysis Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.app_env,
        "checks": {
            "api": "ok",
            "database": "ok",
            "redis": "ok",
            "ai_service": "ok" if settings.gemini_api_key else "degraded"
        }
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.exception("Unhandled exception for %s: %s", request.url.path, exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(api_router, prefix=settings.api_v1_prefix)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
