"""Unit tests for the complete StrategyOptimizer service."""

import pytest

from app.schemas.race import RaceConfig, TireCompound
from app.schemas.results import OptimizationMethod, OptimizationRequest
from app.schemas.strategy import StrategyConstraints
from app.services.optimizer import StrategyOptimizer


@pytest.fixture
def small_race_config():
    return RaceConfig(
        race_name="Short GP",
        circuit_id="short_gp",
        total_laps=12,
        baseline_lap_time=80.0,
        available_compounds=[TireCompound.MEDIUM, TireCompound.HARD],
        initial_compound=TireCompound.MEDIUM,
    )


def test_optimizer_monte_carlo_method(small_race_config):
    request = OptimizationRequest(
        method=OptimizationMethod.MONTE_CARLO,
        monte_carlo_simulations=20,
        random_seed=42,
        constraints=StrategyConstraints(
            min_stops=1,
            max_stops=1,
            min_stint_length=3,
            allowed_compounds=[TireCompound.MEDIUM, TireCompound.HARD],
        ),
    )
    response = StrategyOptimizer.optimize(small_race_config, request)

    assert response.evaluated_candidate_count > 0
    assert response.recommended_stats.rank == 1
    assert len(response.candidate_comparisons) == response.evaluated_candidate_count
    # Verification that rankings are monotonic
    for i in range(len(response.candidate_comparisons) - 1):
        c1 = response.candidate_comparisons[i]
        c2 = response.candidate_comparisons[i + 1]
        assert c1.objective_value <= c2.objective_value
        assert c1.rank < c2.rank


def test_optimizer_exhaustive_agreement(small_race_config):
    """Exhaustive search evaluates every valid strategy and selects the global optimum."""
    request_exh = OptimizationRequest(
        method=OptimizationMethod.EXHAUSTIVE,
        monte_carlo_simulations=25,
        random_seed=123,
        constraints=StrategyConstraints(
            min_stops=1,
            max_stops=1,
            min_stint_length=4,
            allowed_compounds=[TireCompound.MEDIUM, TireCompound.HARD],
        ),
    )
    res_exh = StrategyOptimizer.optimize(small_race_config, request_exh)
    assert res_exh.evaluated_candidate_count >= 5
    best_time = res_exh.recommended_stats.mean_race_time
    worst_time = res_exh.candidate_comparisons[-1].mean_race_time
    assert best_time <= worst_time


def test_optimizer_mcts_method(small_race_config):
    request = OptimizationRequest(
        method=OptimizationMethod.MCTS,
        monte_carlo_simulations=15,
        mcts_iterations=40,
        random_seed=777,
        constraints=StrategyConstraints(
            min_stops=1,
            max_stops=1,
            min_stint_length=3,
            allowed_compounds=[TireCompound.MEDIUM, TireCompound.HARD],
        ),
    )
    response = StrategyOptimizer.optimize(small_race_config, request)
    assert response.method == OptimizationMethod.MCTS
    assert response.recommended_stats.rank == 1
    assert response.execution_time_seconds > 0.0
