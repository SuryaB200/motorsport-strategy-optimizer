"""Unit tests for DataTrainer parameter calibration and polynomial regression."""

import os

import pytest

from app.schemas.race import RaceConfig, TireCompound
from app.services.trainer import DataTrainer

DATASET_PATH = "C:/SDM 2 MOTOR/datasets"


def test_train_pit_loss_model():
    """Verify empirical pit loss training from Formula1.sqlite."""
    if not os.path.exists(os.path.join(DATASET_PATH, "archive", "Formula1.sqlite")):
        pytest.skip("Dataset archive not available")

    pit_res = DataTrainer.train_pit_loss_model(DATASET_PATH)
    assert pit_res["sample_count"] > 1000
    assert 20.0 < pit_res["mean_pit_loss"] < 28.0
    assert 20.0 < pit_res["median_pit_loss"] < 28.0
    assert pit_res["safety_car_pit_loss"] < pit_res["mean_pit_loss"]
    assert len(pit_res["circuit_pit_losses"]) > 0


def test_train_safety_car_model():
    """Verify safety car incident rates calculated from Formula1.sqlite."""
    if not os.path.exists(os.path.join(DATASET_PATH, "archive", "Formula1.sqlite")):
        pytest.skip("Dataset archive not available")

    sc_res = DataTrainer.train_safety_car_model(DATASET_PATH)
    assert 0.0 < sc_res["driver_incident_rate"] < 0.01
    assert 0.01 < sc_res["race_incident_probability_per_lap"] < 0.08
    assert sc_res["deployment_given_incident_probability"] >= 0.5


def test_train_tire_degradation_model():
    """Verify scikit-learn polynomial regression fits degradation curves with high R^2."""
    tire_res = DataTrainer.train_tire_degradation_model(DATASET_PATH)
    params = tire_res["parameters"]
    r2_scores = tire_res["r2_scores"]

    for comp in [TireCompound.SOFT, TireCompound.MEDIUM, TireCompound.HARD]:
        assert comp.value in params
        p = params[comp.value]
        assert p["degradation_linear"] > 0.0
        assert p["degradation_quadratic"] > 0.0
        assert r2_scores[comp.value] > 0.95, f"R^2 for {comp.value} was {r2_scores[comp.value]}"


def test_generate_calibrated_race_config():
    """Verify full RaceConfig generation from calibrated parameters."""
    config = DataTrainer.generate_calibrated_race_config(
        circuit_id="silverstone",
        dataset_path=DATASET_PATH,
    )
    assert isinstance(config, RaceConfig)
    assert config.circuit_id == "silverstone"
    assert config.total_laps == 52
    assert config.baseline_lap_time > 80.0
    assert config.safety_car.pit_loss_normal > config.safety_car.pit_loss_safety_car
