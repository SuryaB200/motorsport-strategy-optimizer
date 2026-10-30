"""Sample demonstration script: Run Monte Carlo & MCTS strategy optimization."""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.schemas.race import (
    ObjectiveType,
    RaceConfig,
    TireCompound,
    WeatherConfig,
    WeatherModelType,
)
from app.schemas.results import OptimizationMethod, OptimizationRequest
from app.schemas.strategy import StrategyConstraints
from app.services.optimizer import StrategyOptimizer


def main() -> None:
    print("=" * 96)
    print("MOTORSPORT STRATEGY OPTIMIZER: MONTE CARLO & MCTS COMPARATIVE DEMO")
    print("=" * 96)

    # 50-lap race configuration under stochastic conditions
    config = RaceConfig(
        race_name="Silverstone Grand Prix Optimization",
        circuit_id="silverstone",
        total_laps=50,
        baseline_lap_time=89.0,
        circuit_wear_factor=1.0,
        weather=WeatherConfig(
            model_type=WeatherModelType.MARKOV,
            markov_transition_matrix=[[0.88, 0.12], [0.35, 0.65]],
        ),
        random_seed=42,
    )

    opt_request = OptimizationRequest(
        method=OptimizationMethod.MCTS,
        monte_carlo_simulations=100,
        mcts_iterations=150,
        random_seed=42,
        objective_type=ObjectiveType.EXPECTED_TIME,
        constraints=StrategyConstraints(
            min_stops=1,
            max_stops=2,
            min_stint_length=10,
            allowed_compounds=[TireCompound.SOFT, TireCompound.MEDIUM, TireCompound.HARD],
        ),
    )

    print("\n[1] Race Setup:")
    print(f"    Name                 : {config.race_name}")
    print(f"    Total Laps           : {config.total_laps}")
    print(f"    Baseline Lap Time    : {config.baseline_lap_time:.1f} s")
    print(
        f"    Stochastic Scenarios : {opt_request.monte_carlo_simulations} (Common Random Numbers)"
    )
    print(f"    MCTS Search Budget   : {opt_request.mcts_iterations} iterations")
    print(
        f"    Strategy Constraints : {opt_request.constraints.min_stops} to {opt_request.constraints.max_stops} stops, min stint {opt_request.constraints.min_stint_length} laps"
    )

    print("\n[2] Executing Strategy Optimization Engine...")
    response = StrategyOptimizer.optimize(config=config, request=opt_request)

    print(f"    Completed in {response.execution_time_seconds:.3f} seconds.")
    print(f"    Total Evaluated Candidate Strategies: {response.evaluated_candidate_count}")

    print("\n[3] Strategy Comparison Leaderboard (Ranked by Expected Race Time):")
    print(
        f"    {'Rank':<5} | {'Strategy Name':<32} | {'Mean (s)':<10} | {'Median (s)':<10} | {'StdDev':<7} | {'P95 (s)':<10} | {'95% CI (s)':<22}"
    )
    print("    " + "-" * 105)

    for s in response.candidate_comparisons[:8]:
        ci_str = f"[{s.confidence_interval_95_low:.1f}, {s.confidence_interval_95_high:.1f}]"
        print(
            f"    #{s.rank:<4} | {s.strategy.name[:32]:<32} | {s.mean_race_time:<10.2f} | {s.median_race_time:<10.2f} | {s.std_dev_race_time:<7.2f} | {s.p95_race_time:<10.2f} | {ci_str:<22}"
        )

    winner = response.recommended_stats
    print("\n[4] Recommended Winning Strategy:")
    print(f"    Name           : {winner.strategy.name}")
    print(f"    Starting Tire  : {winner.strategy.initial_compound.value}")
    print(f"    Planned Stops  : {len(winner.strategy.pit_stops)}")
    for idx, ps in enumerate(winner.strategy.pit_stops, 1):
        print(f"      Stop {idx}: Lap {ps.lap} -> Switch to {ps.compound.value}")
    print(
        f"    Expected Time  : {winner.mean_race_time:.2f} s ({winner.mean_race_time / 60.0:.2f} min)"
    )
    print(f"    Standard Dev   : {winner.std_dev_race_time:.2f} s")
    print(
        f"    Time Advantage : {response.candidate_comparisons[-1].mean_race_time - winner.mean_race_time:.2f} s faster than lowest-ranked candidate"
    )

    print("\n" + "=" * 96)
    print("OPTIMIZATION COMPLETED SUCCESSFULLY")
    print("=" * 96)


if __name__ == "__main__":
    main()
