"""CLI script to train and calibrate simulation parameters from uploaded F1 datasets."""

import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.trainer import DataTrainer


def main() -> None:
    print("=" * 80)
    print("MOTORSPORT STRATEGY OPTIMIZER: DATASET TRAINING & PARAMETER CALIBRATION")
    print("=" * 80)

    dataset_path = "C:/SDM 2 MOTOR/datasets"
    output_file = os.path.join(
        str(Path(__file__).resolve().parent.parent),
        "data",
        "calibrated_models.json",
    )

    print(f"\n[1] Training Source Directory: {dataset_path}")
    print(f"    Target Calibrated Model File: {output_file}")

    print("\n[2] Executing Training Pipeline...")
    results = DataTrainer.train_all(dataset_path=dataset_path, output_file=output_file)

    print("\n[3] Pit Stop Model Calibration:")
    pit = results["pit_model"]
    print(f"    Analyzed Pit Stops   : {pit['sample_count']}")
    print(f"    Mean Pit Loss        : {pit['mean_pit_loss']:.2f} s")
    print(f"    Median Pit Loss      : {pit['median_pit_loss']:.2f} s")
    print(f"    StdDev Pit Loss      : {pit['std_pit_loss']:.2f} s")
    print(f"    Safety Car Pit Loss  : {pit['safety_car_pit_loss']:.2f} s")
    print("    Sample Circuit Pit Losses:")
    for circ, val in list(pit["circuit_pit_losses"].items())[:5]:
        print(f"      - {circ:<16}: {val:.2f} s")

    print("\n[4] Safety Car & Incident Model Calibration:")
    sc = results["safety_car_model"]
    print(f"    Driver Incident Rate : {sc['driver_incident_rate']:.6f} per driver-lap")
    print(
        f"    Race Incident Prob   : {sc['race_incident_probability_per_lap']:.4f} per lap (20-car grid)"
    )
    print(
        f"    Deployment Prob      : {sc['deployment_given_incident_probability']:.2f} given incident"
    )
    print(f"    Duration Window      : {sc['min_duration_laps']} - {sc['max_duration_laps']} laps")
    print(f"    Street Multiplier    : {sc['street_circuit_multiplier']:.2f}x incident rate")

    print("\n[5] Tire Degradation Polynomial Regression Fit (R^2 Scores & Coefficients):")
    tire_params = results["tire_model"]["parameters"]
    r2_scores = results["tire_model"]["r2_scores"]
    print(
        f"    {'Compound':<14} | {'Base (s)':<9} | {'Linear d1':<11} | {'Quad d2':<10} | {'R^2 Score':<9}"
    )
    print("    " + "-" * 62)
    for comp, params in tire_params.items():
        r2 = r2_scores.get(comp, 1.0)
        print(
            f"    {comp:<14} | {params['base_pace_offset']:<9.2f} | {params['degradation_linear']:<11.5f} | "
            f"{params['degradation_quadratic']:<10.6f} | {r2:<9.4f}"
        )

    print("\n[6] Calibrated Circuit Presets Generated:")
    for circ_id, c in results["circuits"].items():
        c_type = "Street" if c["is_street_circuit"] else "Permanent"
        print(
            f"    - {c['name']:<34} | ID: {circ_id:<12} | Laps: {c['total_laps']:<3} | Base: {c['baseline_lap_time']:>5.1f}s | Type: {c_type}"
        )

    print("\n" + "=" * 80)
    print("TRAINING & CALIBRATION COMPLETED SUCCESSFULLY")
    print(f"Model saved to: {output_file}")
    print("=" * 80)


if __name__ == "__main__":
    main()
