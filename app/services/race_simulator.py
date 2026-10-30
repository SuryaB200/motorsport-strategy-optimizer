"""Core deterministic single-race simulation engine."""

from typing import Optional

from app.schemas.race import RaceConfig, WeatherState
from app.schemas.simulation import (
    LapTelemetry,
    SafetyCarEvent,
    SingleSimulationResult,
)
from app.schemas.strategy import Strategy
from app.services.race_state import RaceState
from app.services.random_source import RandomSource
from app.services.safety_car import SafetyCarEngine
from app.services.tires import TireModel, TireState
from app.services.weather import WeatherEngine


class RaceSimulator:
    """Executes lap-by-lap motorsport race simulations under stochastic conditions."""

    @staticmethod
    def simulate(
        config: RaceConfig,
        strategy: Strategy,
        random_source: RandomSource,
        weather_trajectory: Optional[list[WeatherState]] = None,
        safety_car_events: Optional[list[SafetyCarEvent]] = None,
        record_telemetry: bool = True,
    ) -> SingleSimulationResult:
        """Execute a complete race simulation for the given strategy.

        Args:
            config: Validated race configuration.
            strategy: Candidate pit-stop strategy.
            random_source: Independent PRNG.
            weather_trajectory: Optional pre-generated weather sequence.
            safety_car_events: Optional pre-generated Safety Car events.
            record_telemetry: If True, full lap telemetry is retained.

        Returns:
            SingleSimulationResult containing complete race telemetry and summary metrics.
        """
        # 1. Validate strategy against race configuration
        strategy.validate_against_race(
            total_laps=config.total_laps,
            available_compounds=config.available_compounds,
        )

        # 2. Exogenous condition generation if not provided
        if weather_trajectory is None:
            weather_trajectory = WeatherEngine.generate_trajectory(
                config=config.weather,
                total_laps=config.total_laps,
                random_source=random_source,
            )
        elif len(weather_trajectory) != config.total_laps:
            raise ValueError(
                f"Weather trajectory length ({len(weather_trajectory)}) does not match race total laps ({config.total_laps})"
            )

        if safety_car_events is None:
            safety_car_events = SafetyCarEngine.generate_events(
                config=config.safety_car,
                total_laps=config.total_laps,
                random_source=random_source,
            )

        # 3. Initialize race state
        state = RaceState(
            current_lap=1,
            total_elapsed_time=0.0,
            tire_state=TireState(compound=strategy.initial_compound, age_laps=0, set_number=1),
            pit_stop_count=0,
            stint_start_lap=1,
        )

        pit_stop_map = {ps.lap: ps.compound for ps in strategy.pit_stops}
        lap_times: list[float] = []
        telemetry: list[LapTelemetry] = []

        fastest_lap_time = float("inf")
        fastest_lap_number = 1

        # 4. Lap-by-lap simulation loop
        for lap in range(1, config.total_laps + 1):
            sc_active = SafetyCarEngine.is_safety_car_active(safety_car_events, lap)
            weather = weather_trajectory[lap - 1]

            # Tire degradation and weather suitability delta
            tire_delta = TireModel.calculate_total_tire_delta(
                state=state.tire_state,
                compound_params=config.tire_parameters,
                weather=weather,
                circuit_wear_factor=config.circuit_wear_factor,
            )

            # Safety car delta
            sc_delta = config.safety_car.sc_lap_time_delta if sc_active else 0.0

            # Random pace variation
            epsilon = random_source.normal(
                mean=config.pace_variation.mean,
                std_dev=config.pace_variation.std_dev,
            )

            # Nominal on-track lap time with physical lower bound
            on_track_time = config.baseline_lap_time + tire_delta + sc_delta + epsilon
            min_physical_lap = 0.5 * config.baseline_lap_time
            if on_track_time < min_physical_lap:
                on_track_time = min_physical_lap

            # Pit stop check at end of current lap
            pit_stop_taken = lap in pit_stop_map
            pit_time_loss = 0.0
            if pit_stop_taken:
                pit_time_loss = SafetyCarEngine.get_effective_pit_loss(config.safety_car, sc_active)

            total_lap_time = on_track_time + pit_time_loss
            state.total_elapsed_time += total_lap_time
            lap_times.append(total_lap_time)

            if on_track_time < fastest_lap_time:
                fastest_lap_time = on_track_time
                fastest_lap_number = lap

            if record_telemetry:
                telemetry.append(
                    LapTelemetry(
                        lap_number=lap,
                        lap_time=total_lap_time,
                        compound=state.tire_state.compound,
                        tire_age=state.tire_state.age_laps,
                        weather=weather,
                        safety_car_active=sc_active,
                        pit_stop_taken=pit_stop_taken,
                        pit_time_loss=pit_time_loss,
                        cumulative_time=state.total_elapsed_time,
                    )
                )

            # Update tire and stint state
            if pit_stop_taken:
                new_compound = pit_stop_map[lap]
                state.record_pit_stop(lap=lap, new_compound=new_compound)
            else:
                state.tire_state.increment_age()

        # 5. Finalize race stints
        state.finalize_final_stint(total_laps=config.total_laps)

        # 6. Verify total stint laps equals race distance
        total_stint_laps = sum(st.laps_completed for st in state.stints)
        if total_stint_laps != config.total_laps:
            raise ValueError(
                f"Stint lap sum mismatch: calculated {total_stint_laps} vs total race laps {config.total_laps}"
            )

        return SingleSimulationResult(
            race_name=config.race_name,
            circuit_id=config.circuit_id,
            total_laps=config.total_laps,
            strategy=strategy,
            total_race_time=state.total_elapsed_time,
            average_lap_time=state.total_elapsed_time / config.total_laps,
            fastest_lap=fastest_lap_time,
            fastest_lap_number=fastest_lap_number,
            pit_stop_count=state.pit_stop_count,
            pit_stop_laps=[ps.lap for ps in strategy.pit_stops],
            stints=state.stints,
            weather_history=weather_trajectory,
            safety_car_events=safety_car_events,
            final_tire_compound=state.tire_state.compound,
            final_tire_age=state.tire_state.age_laps,
            simulation_seed=random_source.seed,
            telemetry=telemetry,
        )
