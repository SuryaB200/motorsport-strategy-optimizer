"""Unit tests for RaceConfig and parameter validation."""

import pytest
from pydantic import ValidationError

from app.schemas.race import (
    RaceConfig,
    SafetyCarConfig,
    TireCompound,
    WeatherConfig,
    WeatherModelType,
)


def test_default_race_config_valid():
    """Verify default synthetic configuration satisfies all validation constraints."""
    config = RaceConfig()
    assert config.total_laps == 50
    assert config.baseline_lap_time == 90.0
    assert config.initial_compound == TireCompound.MEDIUM
    assert len(config.available_compounds) == 5
    assert config.weather.model_type == WeatherModelType.MARKOV


def test_invalid_total_laps():
    """Total laps must be bounded within [5, 100]."""
    with pytest.raises(ValidationError):
        RaceConfig(total_laps=2)

    with pytest.raises(ValidationError):
        RaceConfig(total_laps=250)


def test_invalid_baseline_lap_time():
    """Baseline lap time must be positive (> 10s)."""
    with pytest.raises(ValidationError):
        RaceConfig(baseline_lap_time=-10.0)

    with pytest.raises(ValidationError):
        RaceConfig(baseline_lap_time=0.0)


def test_markov_matrix_row_stochasticity_validation():
    """Markov transition matrix rows must sum to 1.0 within numerical tolerance."""
    # Invalid: row 0 sums to 1.2
    invalid_matrix = [[0.8, 0.4], [0.3, 0.7]]
    with pytest.raises(ValidationError):
        WeatherConfig(markov_transition_matrix=invalid_matrix)

    # Valid: sums within tolerance
    valid_matrix = [[0.85, 0.15], [0.25, 0.75]]
    w = WeatherConfig(markov_transition_matrix=valid_matrix)
    assert w.markov_transition_matrix == valid_matrix


def test_safety_car_durations_validation():
    """Safety car min duration cannot exceed max duration."""
    with pytest.raises(ValidationError):
        SafetyCarConfig(min_duration_laps=6, max_duration_laps=3)


def test_safety_car_pit_loss_validation():
    """Pit loss during SC cannot exceed normal pit loss."""
    with pytest.raises(ValidationError):
        SafetyCarConfig(pit_loss_normal=20.0, pit_loss_safety_car=25.0)


def test_initial_compound_must_be_in_available_compounds():
    """Initial compound must be one of available compounds."""
    with pytest.raises(ValidationError):
        RaceConfig(
            available_compounds=[TireCompound.HARD, TireCompound.MEDIUM],
            initial_compound=TireCompound.SOFT,
        )


def test_missing_tire_parameters():
    """Every available compound must have corresponding degradation parameters."""
    params = {}  # empty
    with pytest.raises(ValidationError):
        RaceConfig(
            available_compounds=[TireCompound.SOFT],
            initial_compound=TireCompound.SOFT,
            tire_parameters=params,
        )
