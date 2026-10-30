"""Regression tests guarding against edge cases and numerical anomalies."""

from app.schemas.race import RaceConfig, SafetyCarConfig, TireCompound, WeatherState
from app.schemas.strategy import PitStopDecision, Strategy
from app.services.race_simulator import RaceSimulator
from app.services.random_source import RandomSource
from app.services.safety_car import SafetyCarEngine


def test_regression_safety_car_extends_past_final_lap():
    """Ensure Safety Car deployment near finish does not index out of bounds or distort lap count."""
    config = SafetyCarConfig(
        incident_probability_per_lap=1.0,  # guaranteed
        deployment_given_incident_probability=1.0,
        min_duration_laps=10,
        max_duration_laps=10,
    )
    rng = RandomSource(seed=42)
    # 15 lap race: incident on lap 12 with duration 10 would reach lap 21, but race finishes at 15
    events = SafetyCarEngine.generate_events(config, total_laps=15, random_source=rng)

    for e in events:
        assert e.end_lap <= 15
        assert e.duration_laps <= 15


def test_regression_zero_stop_strategy():
    """A 0-stop strategy must complete all laps on the initial tire set without errors."""
    config = RaceConfig(total_laps=25, baseline_lap_time=90.0)
    strat = Strategy(name="0-Stop Hard", initial_compound=TireCompound.HARD, pit_stops=[])
    rng = RandomSource(seed=55)

    res = RaceSimulator.simulate(config, strat, rng, record_telemetry=True)
    assert res.pit_stop_count == 0
    assert len(res.stints) == 1
    assert res.stints[0].laps_completed == 25
    assert res.final_tire_age == 25


def test_regression_pit_stop_on_penultimate_lap():
    """Pit stop on lap total_laps - 1 must execute and final 1-lap stint must record correctly."""
    config = RaceConfig(total_laps=20, baseline_lap_time=90.0)
    strat = Strategy(
        initial_compound=TireCompound.MEDIUM,
        pit_stops=[PitStopDecision(lap=19, compound=TireCompound.SOFT)],
    )
    rng = RandomSource(seed=77)

    res = RaceSimulator.simulate(config, strat, rng, record_telemetry=True)
    assert res.pit_stop_count == 1
    assert len(res.stints) == 2
    assert res.stints[0].laps_completed == 19
    assert res.stints[1].laps_completed == 1
    assert res.final_tire_compound == TireCompound.SOFT
    assert res.final_tire_age == 1


def test_regression_zero_pace_variation():
    """When pace variation std_dev is 0.0, identical conditions produce exactly identical lap times."""
    config = RaceConfig(
        total_laps=10,
        baseline_lap_time=80.0,
    )
    config.pace_variation.std_dev = 0.0

    strat = Strategy(initial_compound=TireCompound.HARD, pit_stops=[])
    dry_weather = [WeatherState.DRY] * 10

    rng1 = RandomSource(seed=1)
    rng2 = RandomSource(seed=2)

    res1 = RaceSimulator.simulate(
        config, strat, rng1, weather_trajectory=dry_weather, safety_car_events=[]
    )
    res2 = RaceSimulator.simulate(
        config, strat, rng2, weather_trajectory=dry_weather, safety_car_events=[]
    )

    assert res1.total_race_time == res2.total_race_time


def test_regression_monsoon_wet_race():
    """All-wet race must run without numerical instability."""
    config = RaceConfig(total_laps=15, baseline_lap_time=95.0)
    strat = Strategy(initial_compound=TireCompound.WET, pit_stops=[])
    wet_weather = [WeatherState.RAIN] * 15
    rng = RandomSource(seed=99)

    res = RaceSimulator.simulate(
        config, strat, rng, weather_trajectory=wet_weather, safety_car_events=[]
    )
    assert res.total_race_time > 0.0
    assert all(w == WeatherState.RAIN for w in res.weather_history)
