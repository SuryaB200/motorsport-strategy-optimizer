"""API tests for the calibration and dataset training endpoints."""


def test_train_endpoint(client):
    res = client.post("/api/v1/calibration/train", json={"dataset_path": "C:/SDM 2 MOTOR/datasets"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert "silverstone" in data["calibrated_circuits"]
    assert "SOFT" in data["tire_regression_scores"]
    assert data["pit_loss_model"]["mean_pit_loss"] > 0


def test_get_calibrated_parameters(client):
    res = client.get("/api/v1/calibration/parameters")
    assert res.status_code == 200
    data = res.json()
    assert "pit_model" in data
    assert "tire_model" in data
    assert "circuits" in data


def test_list_calibrated_circuits(client):
    res = client.get("/api/v1/calibration/circuits")
    assert res.status_code == 200
    circuits = res.json()
    assert "monza" in circuits
    assert "silverstone" in circuits
    assert "spa" in circuits


def test_create_calibrated_race_endpoint(client):
    res = client.post("/api/v1/calibration/races/monza")
    assert res.status_code == 201
    data = res.json()
    assert data["circuit_id"] == "monza"
    assert data["config"]["total_laps"] == 53
    assert data["race_id"] is not None


def test_create_calibrated_race_invalid_circuit(client):
    res = client.post("/api/v1/calibration/races/nonexistent_track")
    assert res.status_code == 404
