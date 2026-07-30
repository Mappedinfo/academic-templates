#!/usr/bin/env python3
"""Main result figure for the paper. Code-drawn from real experiment data
(results.csv produced by your experiment pipeline), never hand-edited."""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
plt.style.use(HERE / "matplotlib-style.mplstyle")


def main() -> None:
    data_path = HERE / "results.csv"
    if not data_path.exists():
        print(f"fill {data_path} with columns: method,metric")
        return
    rows = list(csv.DictReader(data_path.open(encoding="utf-8")))
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.bar([r["method"] for r in rows], [float(r["metric"]) for r in rows])
    ax.set_ylabel("metric")
    out = HERE.parent / "figures" / "main-result.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
