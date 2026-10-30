"""Pydantic V2 schemas for pit stop strategies and constraint definitions."""

from typing import Annotated

from pydantic import BaseModel, Field, model_validator

from app.schemas.race import TireCompound


class PitStopDecision(BaseModel):
    """Specification of a single pit stop event."""

    lap: Annotated[int, Field(ge=1, description="Lap at the end of which the pit stop is taken.")]
    compound: TireCompound = Field(description="Tire compound fitted during the pit stop.")


class Strategy(BaseModel):
    """Full race pit-stop and tire strategy specification."""

    name: str = Field(
        default="Custom Strategy", description="Human-readable name or identifier for the strategy."
    )
    initial_compound: TireCompound = Field(
        description="Tire compound fitted at the start of the race."
    )
    pit_stops: list[PitStopDecision] = Field(
        default_factory=list, description="Chronologically ordered sequence of planned pit stops."
    )

    @model_validator(mode="after")
    def validate_pit_stop_chronology(self) -> "Strategy":
        laps = [ps.lap for ps in self.pit_stops]
        if len(laps) != len(set(laps)):
            raise ValueError(
                "Duplicate pit stop laps detected; each pit stop must occur on a distinct lap."
            )
        if laps != sorted(laps):
            raise ValueError("Pit stops must be strictly in ascending chronological order.")
        return self

    def validate_against_race(
        self, total_laps: int, available_compounds: list[TireCompound]
    ) -> None:
        """Validate strategy against specific race boundaries and available compounds."""
        if self.initial_compound not in available_compounds:
            raise ValueError(
                f"Initial compound {self.initial_compound.value} is not supported by this race."
            )
        for ps in self.pit_stops:
            if ps.lap < 1 or ps.lap >= total_laps:
                raise ValueError(
                    f"Pit stop lap {ps.lap} is invalid for a race of {total_laps} laps (must be between 1 and {total_laps - 1})."
                )
            if ps.compound not in available_compounds:
                raise ValueError(
                    f"Pit stop compound {ps.compound.value} at lap {ps.lap} is not supported by this race."
                )


class StrategyConstraints(BaseModel):
    """Configurable boundaries for candidate strategy generation and search."""

    min_stops: Annotated[int, Field(default=1, ge=0, le=5)]
    max_stops: Annotated[int, Field(default=3, ge=0, le=5)]
    min_stint_length: Annotated[int, Field(default=5, ge=1, le=50)]
    mandatory_two_compounds: bool = Field(
        default=False,
        description="Whether sporting regulations require using at least two different dry compounds in a dry race.",
    )
    allowed_compounds: list[TireCompound] = Field(
        default_factory=lambda: [TireCompound.SOFT, TireCompound.MEDIUM, TireCompound.HARD]
    )

    @model_validator(mode="after")
    def validate_stop_ranges(self) -> "StrategyConstraints":
        if self.min_stops > self.max_stops:
            raise ValueError(
                f"min_stops ({self.min_stops}) cannot exceed max_stops ({self.max_stops})."
            )
        if not self.allowed_compounds:
            raise ValueError("allowed_compounds cannot be empty.")
        return self
