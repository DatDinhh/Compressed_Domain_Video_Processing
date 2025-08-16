from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

try:
    from cdproc import cdproc_cpp as _cpp  
except Exception:  
    import cdproc_cpp as _cpp  

from cdproc.io import write_features_csv


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Extract compressed-domain features (t,E,S,div) using native decoder."
    )
    ap.add_argument("--video", required=True, help="Path to input video (H.264/HEVC recommended)")
    ap.add_argument("--out", default="features.csv", help="Output CSV path")
    args = ap.parse_args()

    video = str(Path(args.video))
    rows = _cpp.extract_features(video)
    if not rows:
        print("WARNING: extractor returned zero rows. Is the codec supported / vectors available?")

    write_features_csv(rows, args.out)
    print(f"Wrote features to {args.out} ({len(rows)} frames)")


if __name__ == "__main__":
    main()
