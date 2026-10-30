"""Live API client verification script."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

print("=" * 80)
print("LIVE API END-TO-END VERIFICATION")
print("=" * 80)

# 1. Health check
print("\n[TEST 1] GET /health")
r1 = client.get("/health")
print("Status:", r1.status_code)
print("Payload:", r1.json())
assert r1.status_code == 200

# 2. Calibration training
print("\n[TEST 2] POST /api/v1/calibration/train")
r2 = client.post("/api/v1/calibration/train", json={"dataset_path": "C:/SDM 2 MOTOR/datasets"})
print("Status:", r2.status_code)
data2 = r2.json()
print("Calibrated circuits:", data2["calibrated_circuits"])
print("Tire R^2 scores:", data2["tire_regression_scores"])
assert r2.status_code == 200

# 3. Create calibrated race (Monza)
print("\n[TEST 3] POST /api/v1/calibration/races/monza")
r3 = client.post("/api/v1/calibration/races/monza")
print("Status:", r3.status_code)
data3 = r3.json()
race_id = data3["race_id"]
print(f"Created Race ID: {race_id} ({data3['race_name']}, {data3['config']['total_laps']} laps)")
assert r3.status_code == 201

# 4. Run single simulation on Monza
print("\n[TEST 4] POST /api/v1/simulations")
sim_payload = {
    "race_id": race_id,
    "strategy": {
        "name": "Medium-Hard 1-Stop",
        "initial_compound": "MEDIUM",
        "pit_stops": [{"lap": 24, "compound": "HARD"}],
    },
    "random_seed": 42,
    "record_telemetry": True,
}
r4 = client.post("/api/v1/simulations", json=sim_payload)
print("Status:", r4.status_code)
data4 = r4.json()
print(
    f"Total Race Time: {data4['total_race_time']:.2f}s ({data4['total_race_time'] / 60.0:.2f} min)"
)
print(f"Fastest Lap: {data4['fastest_lap']:.3f}s (Lap {data4['fastest_lap_number']})")
print(f"Telemetry laps recorded: {len(data4['telemetry'])}")
assert r4.status_code == 200

# 5. Run MCTS Strategy Optimization
print("\n[TEST 5] POST /api/v1/strategies/optimize")
opt_payload = {
    "race_id": race_id,
    "method": "MCTS",
    "monte_carlo_simulations": 50,
    "mcts_iterations": 100,
    "random_seed": 42,
    "constraints": {
        "min_stops": 1,
        "max_stops": 2,
        "min_stint_length": 12,
        "allowed_compounds": ["SOFT", "MEDIUM", "HARD"],
    },
}
r5 = client.post("/api/v1/strategies/optimize", json=opt_payload)
print("Status:", r5.status_code)
data5 = r5.json()
run_id = data5["run_id"]
print(f"Completed Optimization in {data5['execution_time_seconds']}s")
print(f"Evaluated candidates: {data5['evaluated_candidate_count']}")
winner = data5["recommended_stats"]
print(f"Recommended Strategy: {winner['strategy']['name']}")
print(
    f"Expected Race Time: {winner['mean_race_time']:.2f}s (StdDev: {winner['std_dev_race_time']:.2f}s)"
)
assert r5.status_code == 200

# 6. Retrieve comparisons from SQLite
print(f"\n[TEST 6] GET /api/v1/results/{run_id}/strategies")
r6 = client.get(f"/api/v1/results/{run_id}/strategies")
print("Status:", r6.status_code)
data6 = r6.json()
print(f"Retrieved {len(data6)} stored strategy comparisons from SQLite.")
print("Top 3 Strategies:")
for s in data6[:3]:
    print(
        f"  Rank #{s['rank']}: {s['strategy']['name']:<30} | Mean Time: {s['mean_race_time']:.2f}s"
    )
assert r6.status_code == 200

print("\n" + "=" * 80)
print("ALL LIVE API VERIFICATION TESTS PASSED SUCCESSFULLY!")
print("=" * 80)
