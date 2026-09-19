from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "NeuraOps AI"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    frontend_url: str = "http://localhost:3000"
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    database_url: str = "sqlite:///./neuraops.db"
    redis_url: str = "redis://localhost:6379/0"
    gemini_api_key: str = ""
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    free_plan_limits: dict[str, int | str] = {
        "max_services": 2,
        "max_logs_per_day": 500,
        "max_incidents_per_day": 5,
        "max_ai_analyses_per_day": 3,
        "dashboard": True,
        "basic_logs": True,
        "basic_metrics": True,
        "basic_incidents": True,
        "advanced_ai_rca": False,
        "advanced_analytics": False,
        "architecture_intelligence": False,
        "advanced_alerts": False,
        "extended_history": False,
        "exports": False,
    }
    pro_plan_limits: dict[str, int | str] = {
        "max_services": -1,
        "max_logs_per_day": -1,
        "max_incidents_per_day": -1,
        "max_ai_analyses_per_day": -1,
        "dashboard": True,
        "basic_logs": True,
        "basic_metrics": True,
        "basic_incidents": True,
        "advanced_ai_rca": True,
        "advanced_analytics": True,
        "architecture_intelligence": True,
        "advanced_alerts": True,
        "extended_history": True,
        "exports": True,
    }
    feature_access_matrix: dict[str, dict[str, bool]] = {
        "dashboard": {"FREE": True, "PRO": True},
        "basic_logs": {"FREE": True, "PRO": True},
        "basic_metrics": {"FREE": True, "PRO": True},
        "basic_incidents": {"FREE": True, "PRO": True},
        "advanced_ai_rca": {"FREE": False, "PRO": True},
        "advanced_analytics": {"FREE": False, "PRO": True},
        "architecture_intelligence": {"FREE": False, "PRO": True},
        "advanced_alerts": {"FREE": False, "PRO": True},
        "extended_history": {"FREE": False, "PRO": True},
        "exports": {"FREE": False, "PRO": True},
    }

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()
