"""Unit tests for StrategyGenerator."""

from app.schemas.race import TireCompound
from app.schemas.strategy import StrategyConstraints
from app.services.strategy_generator import StrategyGenerator


def test_exhaustive_generation_small_race():
    total_laps = 12
    constraints = StrategyConstraints(
        min_stops=1,
        max_stops=1,
        min_stint_length=4,
        allowed_compounds=[TireCompound.MEDIUM, TireCompound.HARD],
        mandatory_two_compounds=True,
    )
    # Stints must be at least 4 laps: Lap 1..L1 (len >= 4), L1+1..12 (len >= 4)
    # L1 can be 4, 5, 6, 7, 8 (5 possible laps)
    # Compounds: (M, H) or (H, M) (2 combinations) -> 5 * 2 = 10 strategies
    candidates = StrategyGenerator.generate_exhaustive(
        total_laps=total_laps,
        constraints=constraints,
        max_candidates=50,
    )

    assert len(candidates) == 10
    for strat in candidates:
        strat.validate_against_race(total_laps, constraints.allowed_compounds)
        assert len(strat.pit_stops) == 1
        assert strat.initial_compound != strat.pit_stops[0].compound


def test_mandatory_two_compounds_filter():
    constraints = StrategyConstraints(
        min_stops=1,
        max_stops=1,
        min_stint_length=5,
        allowed_compounds=[TireCompound.SOFT, TireCompound.MEDIUM],
        mandatory_two_compounds=True,
    )
    candidates = StrategyGenerator.generate_candidates(
        total_laps=30,
        constraints=constraints,
        max_candidates=20,
    )
    for c in candidates:
        used = {c.initial_compound} | {ps.compound for ps in c.pit_stops}
        assert len(used) >= 2


def test_candidate_generation_bounded_by_max():
    constraints = StrategyConstraints(
        min_stops=1,
        max_stops=2,
        min_stint_length=5,
        allowed_compounds=[TireCompound.SOFT, TireCompound.MEDIUM, TireCompound.HARD],
    )
    candidates = StrategyGenerator.generate_candidates(
        total_laps=50,
        constraints=constraints,
        max_candidates=15,
    )
    assert len(candidates) <= 15
