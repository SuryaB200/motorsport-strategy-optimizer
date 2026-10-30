"""End-to-end integration tests verifying complex race scenarios."""

import pytest

from app.schemas.race import (
    RaceConfig,
    TireCompound,
    WeatherState,
)
from app.schemas.simulation import SafetyCarEvent
from app.schemas.strategy import PitStopDecision, Strategy
from app.services.race_simulator import RaceSimulator
from app.services.random_source import RandomSource


def test_full_complex_race_lifecycle():
    """Verify end-to-end simulation containing Dry, Rain, SC, and multiple tire compound changes."""
    total_laps = 35
    baseline = 90.0

    # Ensure both DRY and RAIN occur
    weather_seq = [WeatherState.DRY] * 20 + [WeatherState.RAIN] * 15

    # Guarantee an SC deployment during laps 12 to 14
    sc_event = SafetyCarEvent(event_id="sc-int-1", start_lap=12, end_lap=14, duration_laps=3)

    config = RaceConfig(
        race_name="Complex Integration Grand Prix",
        circuit_id="spa",
        total_laps=total_laps,
        baseline_lap_time=baseline,
        circuit_wear_factor=1.1,
    )

    # Strategy: Start Medium, Pit lap 13 (under SC) to Hard, Pit lap 22 (after rain starts) to Intermediate
    strategy = Strategy(
        name="Adaptive 2-Stop",
        initial_compound=TireCompound.MEDIUM,
        pit_stops=[
            PitStopDecision(lap=13, compound=TireCompound.HARD),
            PitStopDecision(lap=22, compound=TireCompound.INTERMEDIATE),
        ],
    )

    rng = RandomSource(seed=2026)
    result = RaceSimulator.simulate(
        config=config,
        strategy=strategy,
        random_source=rng,
        weather_trajectory=weather_seq,
        safety_car_events=[sc_event],
        record_telemetry=True,
    )

    # 1. Verification of race distance and telemetry completeness
    assert result.total_laps == total_laps
    assert len(result.telemetry) == total_laps

    # 2. Weather condition verification
    assert WeatherState.DRY in result.weather_history
    assert WeatherState.RAIN in result.weather_history

    # 3. Safety car deployment verification
    sc_laps = [t.lap_number for t in result.telemetry if t.safety_car_active]
    assert sc_laps == [12, 13, 14]

    # 4. Pit stop verification
    assert result.pit_stop_count == 2
    assert result.pit_stop_laps == [13, 22]

    # Pit stop 1 on lap 13 was under Safety Car
    pit_lap_13 = result.telemetry[12]
    assert pit_lap_13.pit_stop_taken is True
    assert pit_lap_13.safety_car_active is True
    assert pit_lap_13.pit_time_loss == config.safety_car.pit_loss_safety_car

    # Pit stop 2 on lap 22 was under green flag in Rain
    pit_lap_22 = result.telemetry[21]
    assert pit_lap_22.pit_stop_taken is True
    assert pit_lap_22.safety_car_active is False
    assert pit_lap_22.pit_time_loss == config.safety_car.pit_loss_normal

    # 5. Stints verification
    assert len(result.stints) == 3
    s1, s2, s3 = result.stints
    assert s1.compound == TireCompound.MEDIUM and s1.laps_completed == 13
    assert s2.compound == TireCompound.HARD and s2.laps_completed == 9
    assert s3.compound == TireCompound.INTERMEDIATE and s3.laps_completed == 13
    assert s1.laps_completed + s2.laps_completed + s3.laps_completed == total_laps

    # 6. Tire age reset checks
    # Lap 1: age 0
    assert result.telemetry[0].tire_age == 0
    # Lap 13: age 12
    assert result.telemetry[12].tire_age == 12
    # Lap 14 (first lap of Hard set): age 0
    assert result.telemetry[13].tire_age == 0
    # Lap 23 (first lap of Intermediate set): age 0
    assert result.telemetry[22].tire_age == 0

    # 7. Total time mathematical integrity
    sum_lap_times = sum(t.lap_time for t in result.telemetry)
    assert pytest.approx(result.total_race_time, rel=1e-5) == sum_lap_times
    assert pytest.approx(result.telemetry[-1].cumulative_time, rel=1e-5) == result.total_race_time
    assert result.fastest_lap < result.average_lap_time
