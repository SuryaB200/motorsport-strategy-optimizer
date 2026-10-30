"""Comprehensive API integration tests for all FastAPI endpoints."""


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Motorsport" in data["app_name"]


def test_system_config(client):
    response = client.get("/api/v1/config")
    assert response.status_code == 200
    data = response.json()
    assert "SOFT" in data["supported_compounds"]
    assert "MARKOV" in data["supported_weather_models"]
    assert "limits" in data


def test_create_and_get_race(client):
    race_payload = {
        "race_name": "Silverstone Test",
        "circuit_id": "silverstone",
        "total_laps": 52,
        "baseline_lap_time": 88.5,
    }
    create_res = client.post("/api/v1/races", json=race_payload)
    assert create_res.status_code == 201
    created_data = create_res.json()
    race_id = created_data["race_id"]
    assert created_data["race_name"] == "Silverstone Test"

    # Get race
    get_res = client.get(f"/api/v1/races/{race_id}")
    assert get_res.status_code == 200
    assert get_res.json()["race_id"] == race_id


def test_get_nonexistent_race(client):
    res = client.get("/api/v1/races/nonexistent-race-id")
    assert res.status_code == 404


def test_invalid_race_creation_validation_error(client):
    # Total laps below minimum bound
    bad_payload = {
        "race_name": "Invalid Race",
        "total_laps": 2,
    }
    res = client.post("/api/v1/races", json=bad_payload)
    assert res.status_code == 422


def test_run_simulation_inline_config(client):
    payload = {
        "race_config": {
            "race_name": "Sprint Sim",
            "total_laps": 15,
            "baseline_lap_time": 90.0,
        },
        "strategy": {
            "name": "Soft-Medium",
            "initial_compound": "SOFT",
            "pit_stops": [{"lap": 6, "compound": "MEDIUM"}],
        },
        "random_seed": 42,
        "record_telemetry": True,
    }
    res = client.post("/api/v1/simulations", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["total_laps"] == 15
    assert data["pit_stop_count"] == 1
    assert len(data["telemetry"]) == 15
    assert data["total_race_time"] > 0.0


def test_run_simulation_with_stored_race(client):
    # Create race first
    race_res = client.post("/api/v1/races", json={"total_laps": 10, "baseline_lap_time": 80.0})
    race_id = race_res.json()["race_id"]

    payload = {
        "race_id": race_id,
        "strategy": {
            "initial_compound": "MEDIUM",
            "pit_stops": [{"lap": 5, "compound": "HARD"}],
        },
    }
    res = client.post("/api/v1/simulations", json=payload)
    assert res.status_code == 200
    assert res.json()["total_laps"] == 10


def test_optimize_strategy_and_retrieve_results(client):
    opt_payload = {
        "race_config": {
            "race_name": "Opt Grand Prix",
            "total_laps": 15,
            "baseline_lap_time": 85.0,
        },
        "method": "MONTE_CARLO",
        "monte_carlo_simulations": 25,
        "random_seed": 123,
        "constraints": {
            "min_stops": 1,
            "max_stops": 1,
            "min_stint_length": 4,
            "allowed_compounds": ["MEDIUM", "HARD"],
        },
    }
    res = client.post("/api/v1/strategies/optimize", json=opt_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["method"] == "MONTE_CARLO"
    assert data["recommended_stats"]["rank"] == 1
    assert data["evaluated_candidate_count"] > 0

    run_id = data["run_id"]
    # Retrieve strategies comparisons
    strats_res = client.get(f"/api/v1/results/{run_id}/strategies")
    assert strats_res.status_code == 200
    comparisons = strats_res.json()
    assert len(comparisons) == data["evaluated_candidate_count"]

    first_result_id = comparisons[0]["result_id"]
    single_res = client.get(f"/api/v1/results/{first_result_id}")
    assert single_res.status_code == 200
    assert single_res.json()["result_id"] == first_result_id


def test_missing_result_returns_404(client):
    res = client.get("/api/v1/results/nonexistent-res-id")
    assert res.status_code == 404
