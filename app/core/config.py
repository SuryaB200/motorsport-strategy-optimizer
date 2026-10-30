"""Application settings and limits management."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """System settings loaded from environment or defaults."""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "Motorsport Strategy Optimizer"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'data' / 'motorsport_strategy.db'}"

    # Resource and Guardrail Limits
    MAX_RACE_LAPS: int = Field(default=100, ge=1, le=200)
    MAX_MONTE_CARLO_SIMS: int = Field(default=5000, ge=1, le=50000)
    MAX_MCTS_ITERATIONS: int = Field(default=2000, ge=1, le=10000)
    MAX_CANDIDATE_STRATEGIES: int = Field(default=200, ge=1, le=1000)
    DEFAULT_SEED: int = 42


settings = Settings()
