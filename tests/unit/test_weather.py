"""Unit tests for RandomSource and WeatherEngine."""

import pytest

from app.schemas.race import WeatherConfig, WeatherModelType, WeatherState
from app.services.random_source import RandomSource
from app.services.weather import WeatherEngine


def test_random_source_reproducibility():
    """Identical seeds must produce identical random outputs."""
    rng1 = RandomSource(seed=12345)
    rng2 = RandomSource(seed=12345)

    samples1 = [rng1.uniform() for _ in range(20)]
    samples2 = [rng2.uniform() for _ in range(20)]
    assert samples1 == samples2


def test_weather_engine_bernoulli_trajectory_length_and_determinism():
    config = WeatherConfig(
        model_type=WeatherModelType.BERNOULLI,
        bernoulli_rain_probability=0.3,
        initial_rain_probability=0.3,
    )
    rng1 = RandomSource(seed=999)
    rng2 = RandomSource(seed=999)

    traj1 = WeatherEngine.generate_trajectory(config, total_laps=50, random_source=rng1)
    traj2 = WeatherEngine.generate_trajectory(config, total_laps=50, random_source=rng2)

    assert len(traj1) == 50
    assert traj1 == traj2
    assert all(isinstance(s, WeatherState) for s in traj1)


def test_weather_engine_markov_trajectory_determinism_and_initial_state():
    config = WeatherConfig(
        model_type=WeatherModelType.MARKOV,
        initial_state=WeatherState.RAIN,
        markov_transition_matrix=[[0.9, 0.1], [0.4, 0.6]],
    )
    rng1 = RandomSource(seed=42)
    rng2 = RandomSource(seed=42)

    traj1 = WeatherEngine.generate_trajectory(config, total_laps=60, random_source=rng1)
    traj2 = WeatherEngine.generate_trajectory(config, total_laps=60, random_source=rng2)

    assert len(traj1) == 60
    assert traj1[0] == WeatherState.RAIN
    assert traj1 == traj2


def test_weather_engine_invalid_total_laps():
    config = WeatherConfig()
    rng = RandomSource(seed=1)
    with pytest.raises(ValueError, match="total_laps must be positive"):
        WeatherEngine.generate_trajectory(config, total_laps=0, random_source=rng)
