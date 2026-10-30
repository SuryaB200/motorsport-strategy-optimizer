"""Race state tracking model during execution of a race simulation."""

from dataclasses import dataclass, field

from app.schemas.race import TireCompound
from app.schemas.simulation import LapTelemetry, TireStint
from app.services.tires import TireState


@dataclass
class RaceState:
    """Encapsulates the mutable dynamic state of a racing car and race conditions."""

    current_lap: int = 1
    total_elapsed_time: float = 0.0
    tire_state: TireState = field(default_factory=lambda: TireState(compound=TireCompound.MEDIUM))
    pit_stop_count: int = 0
    stint_start_lap: int = 1
    stints: list[TireStint] = field(default_factory=list)
    lap_history: list[LapTelemetry] = field(default_factory=list)

    def record_pit_stop(self, lap: int, new_compound: TireCompound) -> None:
        """Close current tire stint and initialize new stint."""
        completed_stint = TireStint(
            stint_number=len(self.stints) + 1,
            compound=self.tire_state.compound,
            start_lap=self.stint_start_lap,
            end_lap=lap,
            laps_completed=lap - self.stint_start_lap + 1,
        )
        self.stints.append(completed_stint)
        self.pit_stop_count += 1
        self.tire_state.reset(new_compound=new_compound)
        self.stint_start_lap = lap + 1

    def finalize_final_stint(self, total_laps: int) -> None:
        """Close the final stint covering through the end of the race."""
        if self.stint_start_lap <= total_laps:
            final_stint = TireStint(
                stint_number=len(self.stints) + 1,
                compound=self.tire_state.compound,
                start_lap=self.stint_start_lap,
                end_lap=total_laps,
                laps_completed=total_laps - self.stint_start_lap + 1,
            )
            self.stints.append(final_stint)
