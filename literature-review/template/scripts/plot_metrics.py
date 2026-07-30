#!/usr/bin/env python3
"""Plot quantitative comparison from data recorded during the review.
Rule: figures must be code-drawn from real data (numbers copied from the
original papers into metrics.csv), never screenshots or hand sketches."""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
plt.style.use(HERE / "matplotlib-style.mplstyle")


def main() -> None:
    data_path = HERE / "metrics.csv"
    if not data_path.exists():
        print(f"fill {data_path} with columns: work,metric_name,value")
        return
    rows = list(csv.DictReader(data_path.open(encoding="utf-8")))
    works = [r["work"] for r in rows]
    values = [float(r["value"]) for r in rows]
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.bar(works, values)
    ax.set_ylabel(rows[0]["metric_name"] if rows else "metric")
    fig.savefig(HERE.parent / "figures" / "metrics.pdf")
    print("wrote figures/metrics.pdf")


if __name__ == "__main__":
    main()
