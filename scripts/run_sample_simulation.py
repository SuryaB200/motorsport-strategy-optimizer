"""Sample demonstration script: Run a complete stochastic race simulation."""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.schemas.race import RaceConfig, TireCompound
from app.schemas.strategy import PitStopDecision, Strategy
from app.services.race_simulator import RaceSimulator
from app.services.random_source import RandomSource


def main() -> None:
    print("=" * 80)
    print("MOTORSPORT STRATEGY OPTIMIZER: SINGLE RACE SIMULATION DEMO")
    print("=" * 80)

    # 50-lap Grand Prix configuration
    config = RaceConfig(
        race_name="Albert Park Grand Prix",
        circuit_id="albert_park",
        total_laps=50,
        baseline_lap_time=86.0,
        circuit_wear_factor=1.05,
        random_seed=2026,
    )

    # Strategy: Start on Medium, pit on lap 20 for Hard tires (1-Stop)
    strategy = Strategy(
        name="Medium -> Hard 1-Stop",
        initial_compound=TireCompound.MEDIUM,
        pit_stops=[PitStopDecision(lap=20, compound=TireCompound.HARD)],
    )

    rng = RandomSource(seed=config.random_seed)
    print(f"\n[1] Simulating Race: {config.race_name} ({config.total_laps} Laps)")
    print(
        f"    Baseline Pace: {config.baseline_lap_time:.1f}s | Circuit Wear Factor: {config.circuit_wear_factor:.2f}"
    )
    print(f"    Strategy: {strategy.name} (Start: {strategy.initial_compound.value})")

    result = RaceSimulator.simulate(
        config=config,
        strategy=strategy,
        random_source=rng,
        record_telemetry=True,
    )

    print("\n[2] Simulation Summary:")
    print(
        f"    Total Race Time   : {result.total_race_time:.3f} s ({result.total_race_time / 60.0:.2f} min)"
    )
    print(f"    Average Lap Time  : {result.average_lap_time:.3f} s")
    print(f"    Fastest Lap       : {result.fastest_lap:.3f} s (Lap {result.fastest_lap_number})")
    print(f"    Total Pit Stops   : {result.pit_stop_count} (at lap {result.pit_stop_laps})")

    print("\n[3] Stint Telemetry Breakdown:")
    print(f"    {'Stint':<7} | {'Compound':<12} | {'Laps':<12} | {'Duration':<8}")
    print("    " + "-" * 48)
    for st in result.stints:
        print(
            f"    {st.stint_number:<7} | {st.compound.value:<12} | Laps {st.start_lap:>2} - {st.end_lap:<2} | {st.laps_completed:>2} laps"
        )

    print("\n[4] Stochastic Conditions Realized:")
    rain_laps = [idx + 1 for idx, w in enumerate(result.weather_history) if w.value == "RAIN"]
    print(f"    Rain Occurrences  : {len(rain_laps)} laps {rain_laps if rain_laps else '(None)'}")
    print(f"    Safety Car Events : {len(result.safety_car_events)} deployed")
    for sc in result.safety_car_events:
        print(
            f"      - {sc.event_id}: Laps {sc.start_lap} to {sc.end_lap} ({sc.duration_laps} laps)"
        )

    print("\n[5] Sample Telemetry Samples:")
    print(
        f"    {'Lap':<5} | {'Pace (s)':<10} | {'Tire':<8} | {'Age':<5} | {'Weather':<8} | {'SC Active':<10} | {'Cumulative (s)':<14}"
    )
    print("    " + "-" * 72)
    sample_indices = [0, 9, 19, 20, 29, 39, 49]
    for idx in sample_indices:
        t = result.telemetry[idx]
        sc_str = "YES" if t.safety_car_active else "No"
        print(
            f"    {t.lap_number:<5} | {t.lap_time:<10.3f} | {t.compound.value:<8} | {t.tire_age:<5} | {t.weather.value:<8} | {sc_str:<10} | {t.cumulative_time:<14.2f}"
        )

    print("\n" + "=" * 80)
    print("SIMULATION COMPLETED SUCCESSFULLY")
    print("=" * 80)


if __name__ == "__main__":
    main()
