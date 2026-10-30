"""Monte Carlo simulation engine supporting Common Random Numbers (CRN) evaluation."""

from dataclasses import dataclass

from app.schemas.race import ObjectiveType, RaceConfig, WeatherState
from app.schemas.results import StrategySummaryStats
from app.schemas.simulation import SafetyCarEvent
from app.schemas.strategy import Strategy
from app.services.race_simulator import RaceSimulator
from app.services.random_source import RandomSource
from app.services.safety_car import SafetyCarEngine
from app.services.statistics import SimulationStatistics
from app.services.weather import WeatherEngine


@dataclass
class RaceScenario:
    """Pre-generated realization of exogenous stochastic events."""

    scenario_id: int
    weather_trajectory: list[WeatherState]
    safety_car_events: list[SafetyCarEvent]
    pace_seed: int


class MonteCarloEngine:
    """Evaluates motorsport strategies across stochastic Monte Carlo scenarios."""

    @staticmethod
    def generate_scenarios(
        config: RaceConfig,
        count: int,
        random_source: RandomSource,
    ) -> list[RaceScenario]:
        """Pre-generate a fixed collection of exogenous race scenarios (Common Random Numbers).

        Args:
            config: Race configuration.
            count: Number of independent scenarios to generate.
            random_source: Master random source.

        Returns:
            List of RaceScenario objects.
        """
        if count <= 0:
            raise ValueError(f"Simulation count must be positive, got {count}")

        scenarios: list[RaceScenario] = []
        child_rngs = random_source.spawn(count)

        for idx, child_rng in enumerate(child_rngs):
            weather = WeatherEngine.generate_trajectory(
                config=config.weather,
                total_laps=config.total_laps,
                random_source=child_rng,
            )
            sc_events = SafetyCarEngine.generate_events(
                config=config.safety_car,
                total_laps=config.total_laps,
                random_source=child_rng,
            )
            pace_seed = child_rng.integers(1, 2**31 - 1)

            scenarios.append(
                RaceScenario(
                    scenario_id=idx + 1,
                    weather_trajectory=weather,
                    safety_car_events=sc_events,
                    pace_seed=pace_seed,
                )
            )

        return scenarios

    @staticmethod
    def evaluate_strategy(
        config: RaceConfig,
        strategy: Strategy,
        scenarios: list[RaceScenario],
    ) -> list[float]:
        """Simulate a single strategy across a set of scenarios and return completed race times."""
        times: list[float] = []
        for scen in scenarios:
            pace_rng = RandomSource(seed=scen.pace_seed)
            result = RaceSimulator.simulate(
                config=config,
                strategy=strategy,
                random_source=pace_rng,
                weather_trajectory=scen.weather_trajectory,
                safety_car_events=scen.safety_car_events,
                record_telemetry=False,
            )
            times.append(result.total_race_time)
        return times

    @staticmethod
    def evaluate_candidates(
        config: RaceConfig,
        candidates: list[Strategy],
        scenarios: list[RaceScenario],
        objective_type: ObjectiveType = ObjectiveType.EXPECTED_TIME,
        risk_aversion_lambda: float = 0.0,
    ) -> list[StrategySummaryStats]:
        """Evaluate and rank all candidate strategies under identical stochastic scenarios."""
        if not candidates:
            raise ValueError("No candidate strategies provided for evaluation.")

        summaries: list[StrategySummaryStats] = []
        for candidate in candidates:
            race_times = MonteCarloEngine.evaluate_strategy(
                config=config,
                strategy=candidate,
                scenarios=scenarios,
            )
            summary = SimulationStatistics.compute_summary(
                strategy=candidate,
                race_times=race_times,
                objective_type=objective_type,
                risk_aversion_lambda=risk_aversion_lambda,
                rank=1,  # will be updated after sorting
            )
            summaries.append(summary)

        # Sort ascending by objective_value (lower race time is superior)
        summaries.sort(key=lambda s: s.objective_value)

        # Update ranks
        for rank_idx, summary in enumerate(summaries, start=1):
            summary.rank = rank_idx

        return summaries
