"""Inspect notebook models and code cells."""

import json
import os

base_dir = "C:/SDM 2 MOTOR/datasets"

for nb in [
    "f1-safety-car-predictor.ipynb",
    "f1-pit-stop-trends-and-weather-strategy.ipynb",
    "tyre-degradation-analysis-saudi-2025.ipynb",
]:
    path = os.path.join(base_dir, nb)
    print("=" * 60)
    print(f"NOTEBOOK: {nb}")
    print("=" * 60)
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        data = json.load(f)
    cells = data.get("cells", [])
    for idx, c in enumerate(cells):
        ctype = c.get("cell_type")
        source = "".join(c.get("source", []))
        if any(
            term in source.lower()
            for term in [
                "model",
                "fit",
                "regress",
                "train",
                "scikit",
                "degradation",
                "safety",
                "weather",
                "pit",
            ]
        ):
            print(f"Cell {idx} ({ctype}):")
            print(source[:500])
            print("-" * 40)
