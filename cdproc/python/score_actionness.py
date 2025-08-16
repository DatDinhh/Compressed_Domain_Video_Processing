from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from cdproc.io import load_features
from cdproc.features import SmoothParams, compute_actionness
from cdproc.plot import plot_timeline


def main() -> None:
    ap = argparse.ArgumentParser(description="Compute and plot actionness timeline from features.csv")
    ap.add_argument("--features", required=True, help="Path to features.csv")
    ap.add_argument("--timeline", default="timeline.png", help="Output PNG")
    ap.add_argument("--smooth", choices=["ema", "sma"], default="ema", help="Smoothing kind")
    ap.add_argument("--window", type=int, default=5, help="Smoothing span/window")
    ap.add_argument("--wE", type=float, default=1.0, help="Weight for E term")
    ap.add_argument("--wS", type=float, default=1.0, help="Weight for S term")
    ap.add_argument("--wD", type=float, default=0.25, help="Weight for |Δdiv| term")
    ap.add_argument("--no-deriv", action="store_true", help="Disable |Δdiv| derivative term")
    args = ap.parse_args()

    df = load_features(args.features)
    params = SmoothParams(kind=args.smooth, window=args.window)
    df2 = compute_actionness(
        df,
        smooth_params=params,
        weights=(args.wE, args.wS, args.wD),
        include_derivatives=(not args.no_deriv),
        out_col="actionness",
    )
    plot_timeline(df2, out_path=args.timeline, metric="actionness", shots=None, title="Actionness")
    print(f"Wrote timeline to {args.timeline}")


if __name__ == "__main__":
    main()
