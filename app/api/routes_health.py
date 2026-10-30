"""Health check and system configuration disclosure endpoints."""

from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings
from app.schemas.race import (
    ObjectiveType,
    TireCompound,
    WeatherModelType,
    default_tire_parameters,
)

router = APIRouter(tags=["Health & Configuration"])


class HealthResponse(BaseModel):
    status: str
    app_name: str
    environment: str
    timestamp: str


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Return current server and service health status."""
    return HealthResponse(
        status="healthy",
        app_name=settings.APP_NAME,
        environment=settings.ENVIRONMENT,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/api/v1/config")
def get_system_configuration() -> dict:
    """Return supported modeling parameters, compounds, weather models, and safe limits."""
    return {
        "supported_compounds": [c.value for c in TireCompound],
        "supported_weather_models": [w.value for w in WeatherModelType],
        "supported_objectives": [o.value for o in ObjectiveType],
        "default_tire_parameters": {
            k.value: v.model_dump() for k, v in default_tire_parameters().items()
        },
        "limits": {
            "max_race_laps": settings.MAX_RACE_LAPS,
            "max_monte_carlo_sims": settings.MAX_MONTE_CARLO_SIMS,
            "max_mcts_iterations": settings.MAX_MCTS_ITERATIONS,
            "max_candidate_strategies": settings.MAX_CANDIDATE_STRATEGIES,
        },
    }
