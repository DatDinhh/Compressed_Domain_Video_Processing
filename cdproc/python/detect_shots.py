from __future__ import annotations

import argparse
from pathlib import Path

from cdproc.io import load_features, write_shots_csv
from cdproc.detect import TwoThreshParams, detect_shots


def main() -> None:
    ap = argparse.ArgumentParser(description="Detect shot boundaries from features.csv")
    ap.add_argument("--features", required=True, help="Path to features.csv")
    ap.add_argument("--out", default="shots.csv", help="Output CSV of detected cuts")

    ap.add_argument("--l1", type=float, default=None, help="High absolute threshold (overrides --k1 if set)")
    ap.add_argument("--l2", type=float, default=None, help="Low absolute threshold (overrides --k2 if set)")
    ap.add_argument("--k1", type=float, default=2.5, help="Dynamic high threshold multiplier (mu + k1*std)")
    ap.add_argument("--k2", type=float, default=1.5, help="Dynamic low threshold multiplier (mu + k2*std)")
    ap.add_argument("--tau", type=int, default=3, help="Consecutive frames above low threshold to fire")
    ap.add_argument("--guard", type=int, default=8, help="Refractory frames after a cut")
    ap.add_argument("--wE", type=float, default=1.0, help="Weight for |ΔE|")
    ap.add_argument("--wS", type=float, default=0.6, help="Weight for |ΔS|")
    ap.add_argument("--wD", type=float, default=0.2, help="Weight for |Δdiv|")
    ap.add_argument("--smooth", choices=["ema", "sma"], default="ema", help="Pre-smoothing kind")
    ap.add_argument("--window", type=int, default=3, help="Pre-smoothing window/span")
    args = ap.parse_args()

    df = load_features(args.features)

    params = TwoThreshParams(
        l1=args.l1,
        l2=args.l2,
        k1=args.k1,
        k2=args.k2,
        tau=args.tau,
        guard=args.guard,
        weights=(args.wE, args.wS, args.wD),
    )
    params.smooth_params.kind = args.smooth  # type: ignore
    params.smooth_params.window = args.window

    shots = detect_shots(df, params=params)
    write_shots_csv(shots, args.out)
    print(f"Detected {len(shots)} cuts → {args.out}")


if __name__ == "__main__":
    main()
