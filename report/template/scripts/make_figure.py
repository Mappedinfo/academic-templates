#!/usr/bin/env python3
"""Generate figures for the report. Fonts follow the academic-templates
baseline: Libertinus Sans (Latin) + Noto Sans CJK SC (Chinese)."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
plt.style.use(HERE / "matplotlib-style.mplstyle")


def main() -> None:
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot([1, 2, 3, 4], [0.91, 0.88, 0.86, 0.85], marker="o", label="真实数据 Real data")
    ax.set_xlabel("迭代 Iteration")
    ax.set_ylabel("指标 Metric")
    ax.set_title("示例数据图 Example plot")
    ax.legend()
    out = HERE.parent / "figures" / "example.svg"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
