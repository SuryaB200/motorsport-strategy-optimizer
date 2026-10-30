"""Pydantic V2 schemas for simulation execution requests and telemetry results."""

from pydantic import BaseModel, Field

from app.schemas.race import RaceConfig, TireCompound, WeatherState
from app.schemas.strategy import Strategy


class LapTelemetry(BaseModel):
    """Telemetry recorded for a single simulated race lap."""

    lap_number: int
    lap_time: float
    compound: TireCompound
    tire_age: int
    weather: WeatherState
    safety_car_active: bool
    pit_stop_taken: bool
    pit_time_loss: float = 0.0
    cumulative_time: float


class TireStint(BaseModel):
    """Structured record of a single tire stint during the race."""

    stint_number: int
    compound: TireCompound
    start_lap: int
    end_lap: int
    laps_completed: int


class SafetyCarEvent(BaseModel):
    """Record of a Safety Car deployment period."""

    event_id: str
    start_lap: int
    end_lap: int
    duration_laps: int


class SingleSimulationResult(BaseModel):
    """Complete, self-contained output of a single race simulation."""

    race_name: str
    circuit_id: str
    total_laps: int
    strategy: Strategy
    total_race_time: float
    average_lap_time: float
    fastest_lap: float
    fastest_lap_number: int
    pit_stop_count: int
    pit_stop_laps: list[int]
    stints: list[TireStint]
    weather_history: list[WeatherState]
    safety_car_events: list[SafetyCarEvent]
    final_tire_compound: TireCompound
    final_tire_age: int
    simulation_seed: int
    telemetry: list[LapTelemetry] = Field(default_factory=list)


class SimulationRequest(BaseModel):
    """Request schema for running a single simulation."""

    race_id: str | None = Field(
        default=None, description="ID of a pre-configured race in the database."
    )
    race_config: RaceConfig | None = Field(
        default=None, description="Inline race configuration (used if race_id not provided)."
    )
    strategy: Strategy = Field(description="Candidate strategy to simulate.")
    random_seed: int | None = Field(
        default=None, description="Optional seed for deterministic simulation."
    )
    record_telemetry: bool = Field(
        default=True, description="Whether to include full lap-by-lap telemetry."
    )
