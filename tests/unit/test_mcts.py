"""Unit tests for the MCTS optimization algorithm."""

from app.schemas.race import RaceConfig, TireCompound
from app.schemas.strategy import StrategyConstraints
from app.services.mcts import MCTSEngine
from app.services.random_source import RandomSource


def test_mcts_search_budget_and_validity():
    config = RaceConfig(total_laps=15, baseline_lap_time=85.0)
    constraints = StrategyConstraints(
        min_stops=1,
        max_stops=1,
        min_stint_length=4,
        allowed_compounds=[TireCompound.MEDIUM, TireCompound.HARD],
    )
    mcts = MCTSEngine(config=config, constraints=constraints)
    rng = RandomSource(seed=42)

    strategy = mcts.search(
        initial_compound=TireCompound.MEDIUM,
        iterations=50,
        random_source=rng,
    )

    # Strategy must be legal
    strategy.validate_against_race(config.total_laps, constraints.allowed_compounds)
    assert len(strategy.pit_stops) == 1
    assert 4 <= strategy.pit_stops[0].lap <= 11


def test_mcts_determinism_under_fixed_seed():
    config = RaceConfig(total_laps=12, baseline_lap_time=90.0)
    constraints = StrategyConstraints(
        min_stops=1,
        max_stops=1,
        min_stint_length=3,
        allowed_compounds=[TireCompound.MEDIUM, TireCompound.HARD],
    )

    mcts1 = MCTSEngine(config=config, constraints=constraints)
    mcts2 = MCTSEngine(config=config, constraints=constraints)

    rng1 = RandomSource(seed=99)
    rng2 = RandomSource(seed=99)

    strat1 = mcts1.search(TireCompound.MEDIUM, iterations=40, random_source=rng1)
    strat2 = mcts2.search(TireCompound.MEDIUM, iterations=40, random_source=rng2)

    assert strat1.pit_stops[0].lap == strat2.pit_stops[0].lap
    assert strat1.pit_stops[0].compound == strat2.pit_stops[0].compound
