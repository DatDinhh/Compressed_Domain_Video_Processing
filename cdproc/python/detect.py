from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd

from .features import SmoothParams, diff_abs, smooth


@dataclass
class TwoThreshParams:
    l1: Optional[float] = None
    l2: Optional[float] = None
    k1: float = 2.5          
    k2: float = 1.5          
    tau: int = 3            
    guard: int = 8          
    weights: Tuple[float, float, float] = (1.0, 0.6, 0.2) 
    smooth_params: SmoothParams = SmoothParams("ema", 3)  


def _metric(df: pd.DataFrame, params: TwoThreshParams) -> pd.Series:
    """
    Build a shot-change metric from absolute derivatives of smoothed features.
    M = wE*|ΔE| + wS*|ΔS| + wD*|Δdiv|
    """
    E_s = smooth(df["E"], params.smooth_params)
    S_s = smooth(df["S"], params.smooth_params)
    div_s = smooth(df["div"], params.smooth_params) if "div" in df else pd.Series(np.zeros(len(df)))

    dE = diff_abs(E_s)
    dS = diff_abs(S_s)
    dD = diff_abs(div_s)

    wE, wS, wD = params.weights
    M = wE * dE + wS * dS + wD * dD
    return M.astype("float64")


def _dynamic_thresholds(M: pd.Series, k1: float, k2: float) -> Tuple[float, float]:
    mu = float(M.mean())
    sd = float(M.std(ddof=0))
    l1 = mu + k1 * sd
    l2 = mu + k2 * sd
    return l1, l2


def detect_shots(df_features: pd.DataFrame, params: TwoThreshParams = TwoThreshParams()) -> pd.DataFrame:
    """
    Detect shot boundaries via a two-threshold scheme with guard frames.

    A cut fires if:
      - M[i] >= l1  (immediate), or
      - the last `tau` frames all satisfy M >= l2

    After a cut, skip `guard` frames.

    Returns: DataFrame with columns [frame, t, score, rule]
    """
    if not {"E", "S", "div"}.issubset(df_features.columns):
        missing = {"E", "S", "div"} - set(df_features.columns)
        raise ValueError(f"features DataFrame missing columns: {missing}")

    df = df_features.reset_index(drop=True).copy()
    if "frame" not in df:
        df.insert(0, "frame", range(len(df)))

    M = _metric(df, params)

    # Absolute thresholds, or derive dynamically
    if params.l1 is None or params.l2 is None:
        l1, l2 = _dynamic_thresholds(M, params.k1, params.k2)
    else:
        l1, l2 = float(params.l1), float(params.l2)

    cuts: List[Tuple[int, float, float, str]] = []
    last_cut = -10_000

    for i in range(len(df)):
        if i - last_cut <= params.guard:
            continue
        m = float(M.iat[i])

        if m >= l1:
            cuts.append((int(df.at[i, "frame"]), float(df.at[i, "t"]), m, "high"))
            last_cut = i
            continue

        if i + 1 >= params.tau:
            window = M.iloc[i + 1 - params.tau : i + 1]
            if (window >= l2).all():
                cuts.append((int(df.at[i, "frame"]), float(df.at[i, "t"]), float(window.mean()), "low"))
                last_cut = i

    shots = pd.DataFrame(cuts, columns=["frame", "t", "score", "rule"])
    return shots
