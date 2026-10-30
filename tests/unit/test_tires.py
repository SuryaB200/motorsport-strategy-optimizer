"""Unit tests for tire degradation, age tracking, and compound suitability."""

import pytest

from app.schemas.race import TireCompound, WeatherState, default_tire_parameters
from app.services.tires import TireModel, TireState


@pytest.fixture
def tire_params():
    return default_tire_parameters()


def test_tire_age_progression_and_reset():
    state = TireState(compound=TireCompound.MEDIUM)
    assert state.age_laps == 0
    assert state.set_number == 1

    state.increment_age()
    assert state.age_laps == 1
    state.increment_age()
    assert state.age_laps == 2

    # Pit stop: switch to HARD
    state.reset(new_compound=TireCompound.HARD)
    assert state.compound == TireCompound.HARD
    assert state.age_laps == 0
    assert state.set_number == 2


def test_compound_degradation_ordering(tire_params):
    """At the same tire age, Soft must experience greater degradation than Hard."""
    soft_p = tire_params[TireCompound.SOFT]
    hard_p = tire_params[TireCompound.HARD]

    age = 15
    soft_deg = TireModel.calculate_degradation(age, soft_p)
    hard_deg = TireModel.calculate_degradation(age, hard_p)

    assert soft_deg > hard_deg > 0.0


def test_degradation_non_negative(tire_params):
    hard_p = tire_params[TireCompound.HARD]
    for age in range(0, 40):
        deg = TireModel.calculate_degradation(age, hard_p)
        assert deg >= 0.0


def test_negative_age_raises_error(tire_params):
    hard_p = tire_params[TireCompound.HARD]
    with pytest.raises(ValueError, match="Tire age cannot be negative"):
        TireModel.calculate_degradation(-1, hard_p)


def test_weather_suitability_penalties(tire_params):
    """Soft in rain must incur severe penalty, Wets in dry must incur penalty."""
    soft_p = tire_params[TireCompound.SOFT]
    wet_p = tire_params[TireCompound.WET]

    soft_dry = TireModel.calculate_weather_penalty(TireCompound.SOFT, soft_p, WeatherState.DRY)
    soft_rain = TireModel.calculate_weather_penalty(TireCompound.SOFT, soft_p, WeatherState.RAIN)

    assert soft_dry == 0.0
    assert soft_rain >= 15.0

    wet_dry = TireModel.calculate_weather_penalty(TireCompound.WET, wet_p, WeatherState.DRY)
    wet_rain = TireModel.calculate_weather_penalty(TireCompound.WET, wet_p, WeatherState.RAIN)

    assert wet_dry >= 10.0
    assert wet_rain == 0.0


def test_total_tire_delta_calculation(tire_params):
    state = TireState(compound=TireCompound.MEDIUM, age_laps=10)
    delta_dry = TireModel.calculate_total_tire_delta(
        state=state,
        compound_params=tire_params,
        weather=WeatherState.DRY,
        circuit_wear_factor=1.0,
    )
    # Medium base offset = 0.0, deg = 0.035*10 + 0.0015*100 = 0.35 + 0.15 = 0.50, penalty = 0.0
    assert pytest.approx(delta_dry, rel=1e-3) == 0.50
