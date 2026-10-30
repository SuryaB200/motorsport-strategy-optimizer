"""High-level strategy optimization orchestrator."""

import time
import uuid

from app.schemas.race import RaceConfig
from app.schemas.results import (
    OptimizationMethod,
    OptimizationRequest,
    OptimizationResponse,
)
from app.schemas.strategy import Strategy
from app.services.mcts import MCTSEngine
from app.services.monte_carlo import MonteCarloEngine
from app.services.random_source import RandomSource
from app.services.strategy_generator import StrategyGenerator


class StrategyOptimizer:
    """Orchestrates strategy search, scenario generation, and Monte Carlo evaluation."""

    @staticmethod
    def optimize(
        config: RaceConfig,
        request: OptimizationRequest,
        race_id: str = "transient-race",
    ) -> OptimizationResponse:
        """Run complete strategy optimization according to requested method and constraints.

        Args:
            config: Race configuration.
            request: Optimization options and constraints.
            race_id: Identifier of the race.

        Returns:
            OptimizationResponse with recommended strategy and comparative metrics.
        """
        start_time = time.perf_counter()
        seed = request.random_seed if request.random_seed is not None else config.random_seed
        master_rng = RandomSource(seed=seed)
        run_id = str(uuid.uuid4())
        warnings: list[str] = []

        # 1. Generate common random scenarios for fair evaluation
        num_sims = request.monte_carlo_simulations
        scenarios = MonteCarloEngine.generate_scenarios(
            config=config,
            count=num_sims,
            random_source=master_rng,
        )

        candidates: list[Strategy] = []

        # 2. Candidate generation based on optimization method
        if request.method == OptimizationMethod.EXHAUSTIVE:
            candidates = StrategyGenerator.generate_exhaustive(
                total_laps=config.total_laps,
                constraints=request.constraints,
                max_candidates=100,
            )
            if len(candidates) >= 100:
                warnings.append("Exhaustive search hit candidate ceiling of 100 strategies.")

        elif request.method == OptimizationMethod.MONTE_CARLO:
            candidates = StrategyGenerator.generate_heuristic_grid(
                total_laps=config.total_laps,
                constraints=request.constraints,
                max_candidates=50,
            )

        elif request.method == OptimizationMethod.MCTS:
            # Baseline grid for comparison
            grid_candidates = StrategyGenerator.generate_heuristic_grid(
                total_laps=config.total_laps,
                constraints=request.constraints,
                max_candidates=20,
            )
            candidates.extend(grid_candidates)

            # Run MCTS search for allowed initial compounds
            mcts_engine = MCTSEngine(config=config, constraints=request.constraints)
            for init_comp in request.constraints.allowed_compounds:
                mcts_rng = RandomSource(seed=master_rng.integers(1, 2**31 - 1))
                mcts_strat = mcts_engine.search(
                    initial_compound=init_comp,
                    iterations=request.mcts_iterations,
                    random_source=mcts_rng,
                )
                mcts_strat.name = f"MCTS Discovered ({init_comp.value})"
                # Deduplicate by pit stop profile
                if not any(
                    c.initial_compound == mcts_strat.initial_compound
                    and [(ps.lap, ps.compound) for ps in c.pit_stops]
                    == [(ps.lap, ps.compound) for ps in mcts_strat.pit_stops]
                    for c in candidates
                ):
                    candidates.append(mcts_strat)

        if not candidates:
            # Fallback safe candidate: initial compound, 1 stop at midpoint
            mid_lap = config.total_laps // 2
            fallback_comp = (
                config.available_compounds[1]
                if len(config.available_compounds) > 1
                else config.initial_compound
            )
            candidates.append(
                Strategy(
                    name="Default Midpoint Strategy",
                    initial_compound=config.initial_compound,
                    pit_stops=[{"lap": mid_lap, "compound": fallback_comp}],
                )
            )
            warnings.append(
                "No candidates satisfied constraints; generated default fallback strategy."
            )

        # 3. Fair evaluation under identical stochastic scenarios
        evaluated_summaries = MonteCarloEngine.evaluate_candidates(
            config=config,
            candidates=candidates,
            scenarios=scenarios,
            objective_type=request.objective_type,
            risk_aversion_lambda=request.risk_aversion_lambda,
        )

        # 4. Extract winner
        winner = evaluated_summaries[0]
        elapsed_sec = time.perf_counter() - start_time

        return OptimizationResponse(
            run_id=run_id,
            race_id=race_id,
            method=request.method,
            objective_type=request.objective_type,
            risk_aversion_lambda=request.risk_aversion_lambda,
            recommended_strategy=winner.strategy,
            recommended_stats=winner,
            candidate_comparisons=evaluated_summaries,
            evaluated_candidate_count=len(evaluated_summaries),
            execution_time_seconds=round(elapsed_sec, 3),
            random_seed=seed,
            warnings=warnings,
        )
