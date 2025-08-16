from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")  

import matplotlib.pyplot as plt  
import pandas as pd  


def plot_timeline(
    df: pd.DataFrame,
    out_path: str | Path = "timeline.png",
    metric: str = "actionness",
    shots: Optional[pd.DataFrame] = None,
    title: Optional[str] = None,
) -> None:
    """
    Plot a 1D timeline (metric vs time) and optional vertical lines for shot boundaries.
    - Uses plain matplotlib; no styles or colors set (policy-compliant).
    """
    if metric not in df.columns:
        raise ValueError(f"metric '{metric}' not found in dataframe columns")

    fig = plt.figure(figsize=(10, 3.0))
    ax = fig.add_subplot(111)

    t = df["t"].astype("float64")
    y = df[metric].astype("float64")
    ax.plot(t, y, linewidth=1.2)
    ax.set_xlabel("time (s)")
    ax.set_ylabel(metric)
    if title:
        ax.set_title(title)

    if shots is not None and len(shots) > 0:
        for _, r in shots.iterrows():
            ax.axvline(float(r["t"]), linestyle="--", linewidth=0.8)

    fig.tight_layout()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
