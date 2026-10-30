"""Unit tests for the deterministic RaceSimulator engine."""

import pytest

from app.schemas.race import RaceConfig, TireCompound, WeatherState
from app.schemas.simulation import SafetyCarEvent
from app.schemas.strategy import PitStopDecision, Strategy
from app.services.race_simulator import RaceSimulator
from app.services.random_source import RandomSource


@pytest.fixture
def base_config():
    return RaceConfig(total_laps=30, baseline_lap_time=90.0)


def test_race_simulation_completion_and_telemetry_consistency(base_config):
    strategy = Strategy(
        name="Medium-Hard 1-Stop",
        initial_compound=TireCompound.MEDIUM,
        pit_stops=[PitStopDecision(lap=12, compound=TireCompound.HARD)],
    )
    rng = RandomSource(seed=42)
    result = RaceSimulator.simulate(
        config=base_config,
        strategy=strategy,
        random_source=rng,
        record_telemetry=True,
    )

    assert result.total_laps == 30
    assert len(result.telemetry) == 30
    assert result.pit_stop_count == 1
    assert result.pit_stop_laps == [12]

    # Verify stint breakdown
    assert len(result.stints) == 2
    assert result.stints[0].compound == TireCompound.MEDIUM
    assert result.stints[0].start_lap == 1
    assert result.stints[0].end_lap == 12
    assert result.stints[0].laps_completed == 12

    assert result.stints[1].compound == TireCompound.HARD
    assert result.stints[1].start_lap == 13
    assert result.stints[1].end_lap == 30
    assert result.stints[1].laps_completed == 18

    # Verify total time matches telemetry sum
    sum_lap_times = sum(t.lap_time for t in result.telemetry)
    assert pytest.approx(result.total_race_time, rel=1e-5) == sum_lap_times
    assert pytest.approx(result.telemetry[-1].cumulative_time, rel=1e-5) == result.total_race_time


def test_simulation_determinism_under_fixed_seed(base_config):
    strategy = Strategy(
        initial_compound=TireCompound.SOFT,
        pit_stops=[
            PitStopDecision(lap=8, compound=TireCompound.MEDIUM),
            PitStopDecision(lap=20, compound=TireCompound.HARD),
        ],
    )
    rng1 = RandomSource(seed=101)
    rng2 = RandomSource(seed=101)

    res1 = RaceSimulator.simulate(config=base_config, strategy=strategy, random_source=rng1)
    res2 = RaceSimulator.simulate(config=base_config, strategy=strategy, random_source=rng2)

    assert pytest.approx(res1.total_race_time, rel=1e-6) == res2.total_race_time
    assert [t.lap_time for t in res1.telemetry] == [t.lap_time for t in res2.telemetry]


def test_pit_loss_under_safety_car_applied_correctly(base_config):
    """When pit stop falls on a Safety Car lap, effective SC pit loss must be applied."""
    strategy = Strategy(
        initial_compound=TireCompound.MEDIUM,
        pit_stops=[PitStopDecision(lap=10, compound=TireCompound.HARD)],
    )

    # Force an SC event on laps 9-11
    sc_event = SafetyCarEvent(event_id="sc-test", start_lap=9, end_lap=11, duration_laps=3)
    dry_weather = [WeatherState.DRY] * 30

    rng = RandomSource(seed=1)
    result = RaceSimulator.simulate(
        config=base_config,
        strategy=strategy,
        random_source=rng,
        weather_trajectory=dry_weather,
        safety_car_events=[sc_event],
    )

    pit_lap_telemetry = result.telemetry[9]  # Lap 10 (index 9)
    assert pit_lap_telemetry.pit_stop_taken is True
    assert pit_lap_telemetry.safety_car_active is True
    # Pit loss under SC should equal pit_loss_safety_car (default 12.0s)
    assert pit_lap_telemetry.pit_time_loss == base_config.safety_car.pit_loss_safety_car
