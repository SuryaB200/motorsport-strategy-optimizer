"""Pydantic V2 schemas for race configuration and parameters."""

from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field, field_validator, model_validator


class TireCompound(str, Enum):
    """Supported tire compounds."""

    SOFT = "SOFT"
    MEDIUM = "MEDIUM"
    HARD = "HARD"
    INTERMEDIATE = "INTERMEDIATE"
    WET = "WET"


class WeatherState(str, Enum):
    """Discrete weather states."""

    DRY = "DRY"
    RAIN = "RAIN"


class WeatherModelType(str, Enum):
    """Weather simulation models."""

    BERNOULLI = "BERNOULLI"
    MARKOV = "MARKOV"


class ObjectiveType(str, Enum):
    """Optimization objective functions."""

    EXPECTED_TIME = "EXPECTED_TIME"
    RISK_SENSITIVE = "RISK_SENSITIVE"


class TireCompoundParameters(BaseModel):
    """Parameters governing pace offset and degradation for a specific compound."""

    base_pace_offset: float = Field(
        ...,
        description="Base pace offset in seconds relative to circuit baseline (negative is faster, e.g. Soft=-0.6s).",
    )
    degradation_linear: Annotated[
        float, Field(ge=0.0, description="Linear degradation coefficient d1 (s/lap).")
    ]
    degradation_quadratic: Annotated[
        float, Field(ge=0.0, description="Quadratic degradation coefficient d2 (s/lap^2).")
    ]
    dry_suitability_penalty: Annotated[
        float, Field(ge=0.0, description="Time penalty in seconds when running in DRY conditions.")
    ]
    rain_suitability_penalty: Annotated[
        float, Field(ge=0.0, description="Time penalty in seconds when running in RAIN conditions.")
    ]


def default_tire_parameters() -> dict[TireCompound, TireCompoundParameters]:
    """Default synthetic parameters for all supported compounds."""
    return {
        TireCompound.SOFT: TireCompoundParameters(
            base_pace_offset=-0.8,
            degradation_linear=0.06,
            degradation_quadratic=0.003,
            dry_suitability_penalty=0.0,
            rain_suitability_penalty=18.0,
        ),
        TireCompound.MEDIUM: TireCompoundParameters(
            base_pace_offset=0.0,
            degradation_linear=0.035,
            degradation_quadratic=0.0015,
            dry_suitability_penalty=0.0,
            rain_suitability_penalty=18.0,
        ),
        TireCompound.HARD: TireCompoundParameters(
            base_pace_offset=0.6,
            degradation_linear=0.018,
            degradation_quadratic=0.0008,
            dry_suitability_penalty=0.0,
            rain_suitability_penalty=18.0,
        ),
        TireCompound.INTERMEDIATE: TireCompoundParameters(
            base_pace_offset=3.5,
            degradation_linear=0.08,
            degradation_quadratic=0.004,
            dry_suitability_penalty=6.0,
            rain_suitability_penalty=1.0,
        ),
        TireCompound.WET: TireCompoundParameters(
            base_pace_offset=6.0,
            degradation_linear=0.06,
            degradation_quadratic=0.002,
            dry_suitability_penalty=12.0,
            rain_suitability_penalty=0.0,
        ),
    }


class WeatherConfig(BaseModel):
    """Configuration for weather generation."""

    model_type: WeatherModelType = Field(default=WeatherModelType.MARKOV)
    initial_rain_probability: Annotated[float, Field(default=0.10, ge=0.0, le=1.0)]
    initial_state: WeatherState = Field(default=WeatherState.DRY)
    bernoulli_rain_probability: Annotated[float, Field(default=0.15, ge=0.0, le=1.0)]

    # Markov Transition Matrix: P = [[P(DRY->DRY), P(DRY->RAIN)], [P(RAIN->DRY), P(RAIN->RAIN)]]
    markov_transition_matrix: list[list[float]] = Field(
        default_factory=lambda: [[0.85, 0.15], [0.30, 0.70]]
    )

    @field_validator("markov_transition_matrix")
    @classmethod
    def validate_transition_matrix(cls, matrix: list[list[float]]) -> list[list[float]]:
        if len(matrix) != 2 or any(len(row) != 2 for row in matrix):
            raise ValueError(
                "Markov transition matrix must be exactly 2x2: [[P(D|D), P(R|D)], [P(D|R), P(R|R)]]"
            )

        for r_idx, row in enumerate(matrix):
            for c_idx, val in enumerate(row):
                if val < 0.0 or val > 1.0:
                    raise ValueError(
                        f"Matrix entry [{r_idx}][{c_idx}]={val} is out of probability bounds [0, 1]"
                    )
            row_sum = sum(row)
            if abs(row_sum - 1.0) > 1e-5:
                raise ValueError(
                    f"Matrix row {r_idx} does not sum to 1.0 (sum={row_sum:.6f}) within tolerance 1e-5"
                )
        return matrix


class SafetyCarConfig(BaseModel):
    """Configuration for stochastic Safety Car deployments."""

    incident_probability_per_lap: Annotated[float, Field(default=0.03, ge=0.0, le=1.0)]
    deployment_given_incident_probability: Annotated[float, Field(default=0.75, ge=0.0, le=1.0)]
    min_duration_laps: Annotated[int, Field(default=2, ge=1, le=15)]
    max_duration_laps: Annotated[int, Field(default=5, ge=1, le=20)]
    sc_lap_time_delta: Annotated[
        float,
        Field(default=30.0, ge=0.0, description="Pace delta added per lap under SC (seconds)."),
    ]
    pit_loss_normal: Annotated[
        float,
        Field(
            default=22.0,
            ge=0.0,
            description="Time lost in pit lane under normal green flag (seconds).",
        ),
    ]
    pit_loss_safety_car: Annotated[
        float,
        Field(
            default=12.0,
            ge=0.0,
            description="Effective time lost in pit lane under Safety Car (seconds).",
        ),
    ]

    @model_validator(mode="after")
    def validate_durations_and_losses(self) -> "SafetyCarConfig":
        if self.min_duration_laps > self.max_duration_laps:
            raise ValueError(
                f"min_duration_laps ({self.min_duration_laps}) cannot exceed max_duration_laps ({self.max_duration_laps})"
            )
        if self.pit_loss_safety_car > self.pit_loss_normal:
            raise ValueError(
                f"pit_loss_safety_car ({self.pit_loss_safety_car}) cannot exceed pit_loss_normal ({self.pit_loss_normal})"
            )
        return self


class PaceVariationConfig(BaseModel):
    """Configuration for stochastic lap time variation (epsilon)."""

    mean: float = Field(default=0.0, description="Mean pace error (seconds).")
    std_dev: Annotated[
        float,
        Field(
            default=0.25,
            ge=0.0,
            le=5.0,
            description="Standard deviation of lap pace error (seconds).",
        ),
    ]


class RaceConfig(BaseModel):
    """Complete, validated race configuration specification."""

    race_name: Annotated[str, Field(min_length=1, max_length=128, default="Grand Prix Simulation")]
    circuit_id: Annotated[str, Field(min_length=1, max_length=64, default="synthetic_gp")]
    total_laps: Annotated[
        int, Field(ge=5, le=100, default=50, description="Total race distance in laps.")
    ]
    baseline_lap_time: Annotated[
        float, Field(gt=10.0, le=300.0, default=90.0, description="Nominal lap time in seconds.")
    ]
    circuit_wear_factor: Annotated[
        float, Field(gt=0.1, le=5.0, default=1.0, description="Circuit degradation multiplier.")
    ]
    available_compounds: list[TireCompound] = Field(
        default_factory=lambda: [
            TireCompound.SOFT,
            TireCompound.MEDIUM,
            TireCompound.HARD,
            TireCompound.INTERMEDIATE,
            TireCompound.WET,
        ]
    )
    initial_compound: TireCompound = Field(default=TireCompound.MEDIUM)
    tire_parameters: dict[TireCompound, TireCompoundParameters] = Field(
        default_factory=default_tire_parameters
    )
    weather: WeatherConfig = Field(default_factory=WeatherConfig)
    safety_car: SafetyCarConfig = Field(default_factory=SafetyCarConfig)
    pace_variation: PaceVariationConfig = Field(default_factory=PaceVariationConfig)
    random_seed: int = Field(default=42)

    @model_validator(mode="after")
    def validate_compounds_and_parameters(self) -> "RaceConfig":
        if not self.available_compounds:
            raise ValueError("At least one tire compound must be available.")
        if self.initial_compound not in self.available_compounds:
            raise ValueError(
                f"Initial compound {self.initial_compound.value} is not in available_compounds: "
                f"{[c.value for c in self.available_compounds]}"
            )
        for compound in self.available_compounds:
            if compound not in self.tire_parameters:
                raise ValueError(
                    f"Missing tire degradation parameters for available compound: {compound.value}"
                )
        return self


class RaceConfigCreate(RaceConfig):
    """Schema for creating a new race configuration."""

    pass


class RaceConfigResponse(BaseModel):
    """Response schema containing stored race configuration."""

    race_id: str
    race_name: str
    circuit_id: str
    config: RaceConfig
    created_at: str
