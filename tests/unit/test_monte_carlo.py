"""Unit tests for Monte Carlo simulation engine and statistical evaluation."""

import pytest

from app.schemas.race import ObjectiveType, RaceConfig, TireCompound
from app.schemas.strategy import PitStopDecision, Strategy
from app.services.monte_carlo import MonteCarloEngine
from app.services.random_source import RandomSource
from app.services.statistics import SimulationStatistics


def test_statistics_summary_calculations():
    strat = Strategy(name="Test", initial_compound=TireCompound.MEDIUM, pit_stops=[])
    times = [5000.0, 5020.0, 4980.0, 5010.0, 4990.0]

    summary = SimulationStatistics.compute_summary(
        strategy=strat,
        race_times=times,
        objective_type=ObjectiveType.EXPECTED_TIME,
        risk_aversion_lambda=0.0,
    )

    assert summary.simulation_count == 5
    assert summary.mean_race_time == 5000.0
    assert summary.median_race_time == 5000.0
    assert summary.min_race_time == 4980.0
    assert summary.max_race_time == 5020.0
    assert summary.objective_value == 5000.0


def test_risk_sensitive_objective_penalty():
    strat = Strategy(name="Test", initial_compound=TireCompound.MEDIUM, pit_stops=[])
    times = [4900.0, 5100.0]  # mean = 5000, std = 141.42

    summary_neutral = SimulationStatistics.compute_summary(
        strategy=strat,
        race_times=times,
        objective_type=ObjectiveType.EXPECTED_TIME,
    )
    summary_risk = SimulationStatistics.compute_summary(
        strategy=strat,
        race_times=times,
        objective_type=ObjectiveType.RISK_SENSITIVE,
        risk_aversion_lambda=1.5,
    )

    assert summary_risk.objective_value > summary_neutral.objective_value
    assert pytest.approx(summary_risk.objective_value, rel=1e-3) == (
        summary_neutral.mean_race_time + 1.5 * summary_risk.std_dev_race_time
    )


def test_monte_carlo_crn_fair_comparison():
    config = RaceConfig(total_laps=20, baseline_lap_time=80.0)
    rng = RandomSource(seed=42)

    scenarios = MonteCarloEngine.generate_scenarios(config=config, count=10, random_source=rng)
    assert len(scenarios) == 10

    # Two competing strategies
    strat_a = Strategy(
        name="Strategy A (Medium-Hard)",
        initial_compound=TireCompound.MEDIUM,
        pit_stops=[PitStopDecision(lap=10, compound=TireCompound.HARD)],
    )
    strat_b = Strategy(
        name="Strategy B (Soft-Hard)",
        initial_compound=TireCompound.SOFT,
        pit_stops=[PitStopDecision(lap=6, compound=TireCompound.HARD)],
    )

    results = MonteCarloEngine.evaluate_candidates(
        config=config,
        candidates=[strat_a, strat_b],
        scenarios=scenarios,
    )

    assert len(results) == 2
    assert results[0].rank == 1
    assert results[1].rank == 2
    assert results[0].objective_value <= results[1].objective_value
