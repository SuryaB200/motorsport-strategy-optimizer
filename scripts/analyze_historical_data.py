"""Analyze empirical parameters from Formula1.sqlite."""

import sqlite3

import numpy as np

conn = sqlite3.connect("C:/SDM 2 MOTOR/datasets/archive/Formula1.sqlite")
cur = conn.cursor()

print("=" * 60)
print("1. PIT STOP DURATION ANALYSIS")
print("=" * 60)
cur.execute(
    "SELECT milliseconds / 1000.0 FROM pitstops WHERE milliseconds > 10000 AND milliseconds < 60000"
)
pit_times = [r[0] for r in cur.fetchall()]
if pit_times:
    mean_pit = np.mean(pit_times)
    median_pit = np.median(pit_times)
    std_pit = np.std(pit_times)
    print(f"Sample count : {len(pit_times)}")
    print(f"Mean pit time: {mean_pit:.2f} s")
    print(f"Median pit   : {median_pit:.2f} s")
    print(f"StdDev pit   : {std_pit:.2f} s")

print("\n" + "=" * 60)
print("2. CIRCUIT CHARACTERISTICS (TOP 10 CIRCUITS)")
print("=" * 60)
query = """
SELECT c.circuitRef, c.name, count(distinct r.raceId) as race_count, max(r.year) as last_year
FROM circuits c
JOIN races r ON c.circuitId = r.circuitId
GROUP BY c.circuitId
ORDER BY race_count DESC
LIMIT 10;
"""
cur.execute(query)
for row in cur.fetchall():
    print(f"Circuit: {row[0]:<15} | Races: {row[2]:<3} | Last: {row[3]} | Name: {row[1]}")

print("\n" + "=" * 60)
print("3. LAP TIME DEGRADATION EXTRACTION FROM LAPTIMES & PITSTOPS")
print("=" * 60)
# Look at modern races (post 2011 when pitstop data began)
cur.execute("""
SELECT r.raceId, r.year, c.circuitRef, count(distinct l.driverId)
FROM races r
JOIN circuits c ON r.circuitId = c.circuitId
JOIN laptimes l ON r.raceId = l.raceId
WHERE r.year >= 2015
GROUP BY r.raceId
ORDER BY r.year DESC, r.round DESC
LIMIT 5;
""")
recent_races = cur.fetchall()
for rr in recent_races:
    print(f"Race ID: {rr[0]} | Year: {rr[1]} | Circuit: {rr[2]} | Drivers: {rr[3]}")

conn.close()
