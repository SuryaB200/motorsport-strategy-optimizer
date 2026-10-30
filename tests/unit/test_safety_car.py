"""Unit tests for Safety Car event generation and pit loss calculations."""

from app.schemas.race import SafetyCarConfig
from app.services.random_source import RandomSource
from app.services.safety_car import SafetyCarEngine


def test_safety_car_events_within_bounds_and_no_overlap():
    config = SafetyCarConfig(
        incident_probability_per_lap=0.15,
        deployment_given_incident_probability=1.0,
        min_duration_laps=2,
        max_duration_laps=4,
    )
    rng = RandomSource(seed=123)
    total_laps = 50

    events = SafetyCarEngine.generate_events(config, total_laps=total_laps, random_source=rng)

    for i, event in enumerate(events):
        assert 1 <= event.start_lap <= total_laps
        assert 1 <= event.end_lap <= total_laps
        assert event.start_lap <= event.end_lap
        assert event.duration_laps == (event.end_lap - event.start_lap + 1)

        # Check no overlap with next event
        if i + 1 < len(events):
            next_event = events[i + 1]
            assert event.end_lap < next_event.start_lap


def test_safety_car_is_active_check():
    config = SafetyCarConfig()
    rng = RandomSource(seed=42)
    events = SafetyCarEngine.generate_events(config, total_laps=50, random_source=rng)

    for event in events:
        for lap in range(event.start_lap, event.end_lap + 1):
            assert SafetyCarEngine.is_safety_car_active(events, lap) is True

    # Laps outside events should be False
    all_sc_laps = {lap for e in events for lap in range(e.start_lap, e.end_lap + 1)}
    for lap in range(1, 51):
        if lap not in all_sc_laps:
            assert SafetyCarEngine.is_safety_car_active(events, lap) is False


def test_effective_pit_loss():
    config = SafetyCarConfig(pit_loss_normal=22.0, pit_loss_safety_car=12.0)
    assert SafetyCarEngine.get_effective_pit_loss(config, sc_active=False) == 22.0
    assert SafetyCarEngine.get_effective_pit_loss(config, sc_active=True) == 12.0
