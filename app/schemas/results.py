"""Pydantic V2 schemas for optimization requests, statistical summaries, and comparison responses."""

from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field

from app.schemas.race import ObjectiveType, RaceConfig
from app.schemas.strategy import Strategy, StrategyConstraints


class OptimizationMethod(str, Enum):
    """Supported optimization algorithms."""

    MONTE_CARLO = "MONTE_CARLO"
    MCTS = "MCTS"
    EXHAUSTIVE = "EXHAUSTIVE"


class StrategySummaryStats(BaseModel):
    """Statistical summary metrics for a candidate strategy across stochastic runs."""

    strategy: Strategy
    simulation_count: int
    mean_race_time: float
    median_race_time: float
    std_dev_race_time: float
    min_race_time: float
    max_race_time: float
    p95_race_time: float
    confidence_interval_95_low: float
    confidence_interval_95_high: float
    objective_value: float
    rank: int


class OptimizationRequest(BaseModel):
    """Request schema for strategy optimization."""

    race_id: str | None = Field(default=None, description="Stored race ID.")
    race_config: RaceConfig | None = Field(default=None, description="Inline race configuration.")
    method: OptimizationMethod = Field(default=OptimizationMethod.MONTE_CARLO)
    monte_carlo_simulations: Annotated[int, Field(default=200, ge=10, le=5000)]
    mcts_iterations: Annotated[int, Field(default=300, ge=20, le=2000)]
    random_seed: int | None = Field(default=None)
    objective_type: ObjectiveType = Field(default=ObjectiveType.EXPECTED_TIME)
    risk_aversion_lambda: Annotated[float, Field(default=0.0, ge=0.0, le=5.0)]
    constraints: StrategyConstraints = Field(default_factory=StrategyConstraints)


class OptimizationResponse(BaseModel):
    """Response schema containing strategy recommendation and comparative analysis."""

    run_id: str
    race_id: str
    method: OptimizationMethod
    objective_type: ObjectiveType
    risk_aversion_lambda: float
    recommended_strategy: Strategy
    recommended_stats: StrategySummaryStats
    candidate_comparisons: list[StrategySummaryStats]
    evaluated_candidate_count: int
    execution_time_seconds: float
    random_seed: int
    warnings: list[str] = Field(default_factory=list)
