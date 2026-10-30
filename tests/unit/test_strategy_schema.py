"""Unit tests for Strategy schema and validation."""

import pytest
from pydantic import ValidationError

from app.schemas.race import TireCompound
from app.schemas.strategy import PitStopDecision, Strategy, StrategyConstraints


def test_valid_strategy():
    strat = Strategy(
        name="Medium-Hard 1-Stop",
        initial_compound=TireCompound.MEDIUM,
        pit_stops=[PitStopDecision(lap=20, compound=TireCompound.HARD)],
    )
    assert strat.initial_compound == TireCompound.MEDIUM
    assert len(strat.pit_stops) == 1
    assert strat.pit_stops[0].lap == 20


def test_duplicate_pit_stop_laps_rejected():
    with pytest.raises(ValidationError, match="Duplicate pit stop laps"):
        Strategy(
            initial_compound=TireCompound.SOFT,
            pit_stops=[
                PitStopDecision(lap=15, compound=TireCompound.MEDIUM),
                PitStopDecision(lap=15, compound=TireCompound.HARD),
            ],
        )


def test_unsorted_pit_stops_rejected():
    with pytest.raises(ValidationError, match="strictly in ascending chronological order"):
        Strategy(
            initial_compound=TireCompound.SOFT,
            pit_stops=[
                PitStopDecision(lap=25, compound=TireCompound.MEDIUM),
                PitStopDecision(lap=12, compound=TireCompound.HARD),
            ],
        )


def test_validate_against_race_bounds():
    strat = Strategy(
        initial_compound=TireCompound.SOFT,
        pit_stops=[PitStopDecision(lap=52, compound=TireCompound.HARD)],
    )
    # 50 lap race: lap 52 is outside bounds
    with pytest.raises(ValueError, match="Pit stop lap 52 is invalid"):
        strat.validate_against_race(
            total_laps=50, available_compounds=[TireCompound.SOFT, TireCompound.HARD]
        )


def test_validate_against_unsupported_compound():
    strat = Strategy(
        initial_compound=TireCompound.WET,
        pit_stops=[],
    )
    # WET not available
    with pytest.raises(ValueError, match="not supported"):
        strat.validate_against_race(
            total_laps=50, available_compounds=[TireCompound.SOFT, TireCompound.MEDIUM]
        )


def test_strategy_constraints_validation():
    with pytest.raises(ValidationError):
        StrategyConstraints(min_stops=3, max_stops=1)
