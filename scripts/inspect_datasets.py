"""Inspect datasets uploaded in C:/SDM 2 MOTOR/datasets."""

import os
import sqlite3

base_dir = "C:/SDM 2 MOTOR/datasets"

print("=" * 60)
print("INSPECTING DATASETS")
print("=" * 60)

# 1. SQLite Databases
for root, _dirs, files in os.walk(base_dir):
    for f in files:
        if f.endswith(".sqlite") or f.endswith(".db"):
            full_path = os.path.join(root, f)
            print(f"\nDatabase: {full_path}")
            try:
                conn = sqlite3.connect(full_path)
                cur = conn.cursor()
                cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [r[0] for r in cur.fetchall()]
                for t in tables:
                    cur.execute(f'SELECT count(*) FROM "{t}"')
                    cnt = cur.fetchone()[0]
                    cur.execute(f'PRAGMA table_info("{t}")')
                    cols = [c[1] for c in cur.fetchall()]
                    print(f"  Table: {t:<20} Rows: {cnt:<8} Columns: {cols}")
                conn.close()
            except Exception as e:
                print(f"  Error reading {full_path}: {e}")

# 2. CSV Files
for root, _dirs, files in os.walk(base_dir):
    for f in files:
        if f.endswith(".csv"):
            full_path = os.path.join(root, f)
            print(f"\nCSV: {full_path}")
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as fp:
                    header = fp.readline().strip()
                    first_line = fp.readline().strip()
                    print(f"  Header: {header}")
                    print(f"  Sample: {first_line}")
            except Exception as e:
                print(f"  Error reading {full_path}: {e}")
