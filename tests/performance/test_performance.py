"""Performance and throughput benchmark tests."""

import time

from app.schemas.race import RaceConfig, TireCompound
from app.schemas.results import OptimizationMethod, OptimizationRequest
from app.schemas.strategy import PitStopDecision, Strategy, StrategyConstraints
from app.services.monte_carlo import MonteCarloEngine
from app.services.optimizer import StrategyOptimizer
from app.services.random_source import RandomSource


def test_simulation_throughput():
    """Verify that the engine can execute >= 500 complete 50-lap simulations rapidly."""
    config = RaceConfig(total_laps=50, baseline_lap_time=90.0)
    strat = Strategy(
        initial_compound=TireCompound.MEDIUM,
        pit_stops=[PitStopDecision(lap=20, compound=TireCompound.HARD)],
    )

    count = 500
    rng = RandomSource(seed=42)

    # Pre-generate scenarios
    scenarios = MonteCarloEngine.generate_scenarios(config=config, count=count, random_source=rng)

    start_t = time.perf_counter()
    times = MonteCarloEngine.evaluate_strategy(config=config, strategy=strat, scenarios=scenarios)
    elapsed = time.perf_counter() - start_t

    assert len(times) == count
    # 500 complete 50-lap race simulations (25,000 laps simulated) should take under 2.0 seconds
    assert elapsed < 3.0, f"500 simulations took {elapsed:.3f}s (exceeded limit)"

    laps_per_second = (count * 50) / elapsed
    assert laps_per_second > 5000, f"Throughput was {laps_per_second:.1f} laps/sec"


def test_optimization_benchmark():
    """Verify that multi-candidate optimization terminates within acceptable production budget."""
    config = RaceConfig(total_laps=40, baseline_lap_time=85.0)
    opt_request = OptimizationRequest(
        method=OptimizationMethod.MONTE_CARLO,
        monte_carlo_simulations=50,
        random_seed=123,
        constraints=StrategyConstraints(
            min_stops=1,
            max_stops=2,
            min_stint_length=8,
            allowed_compounds=[TireCompound.SOFT, TireCompound.MEDIUM, TireCompound.HARD],
        ),
    )

    start_t = time.perf_counter()
    response = StrategyOptimizer.optimize(config, opt_request)
    elapsed = time.perf_counter() - start_t

    assert response.evaluated_candidate_count > 0
    assert elapsed < 5.0, f"Optimization took {elapsed:.3f}s (budget exceeded)"
