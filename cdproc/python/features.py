from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional, Tuple

import numpy as np
import pandas as pd


@dataclass
class SmoothParams:
    kind: Literal["ema", "sma"] = "ema"
    window: int = 5  


def _ema(series: pd.Series, span: int) -> pd.Series:
    span = max(1, int(span))
    return series.astype("float64").ewm(span=span, adjust=False, min_periods=1).mean()


def _sma(series: pd.Series, window: int) -> pd.Series:
    window = max(1, int(window))
    return series.astype("float64").rolling(window=window, min_periods=1, center=True).mean()


def smooth(series: pd.Series, params: SmoothParams) -> pd.Series:
    if params.kind == "ema":
        return _ema(series, params.window)
    return _sma(series, params.window)


def zscore(x: pd.Series, eps: float = 1e-12) -> pd.Series:
    x = x.astype("float64")
    mu = float(x.mean())
    sd = float(x.std(ddof=0))
    return (x - mu) / (sd + eps)


def diff_abs(x: pd.Series) -> pd.Series:
    y = x.astype("float64").diff().abs()
    y.iloc[0] = 0.0
    return y


def compute_actionness(
    df: pd.DataFrame,
    smooth_params: SmoothParams | None = SmoothParams("ema", 5),
    weights: Tuple[float, float, float] = (1.0, 1.0, 0.25),
    include_derivatives: bool = True,
    out_col: str = "actionness",
) -> pd.DataFrame:
    """
    Heuristic actionness:
      A = z(smooth(E)) * wE + z(smooth(S)) * wS + z(smooth(|Δdiv|)) * wD
    You can disable the |Δdiv| term via include_derivatives=False.

    Returns a new DataFrame with an added column `out_col`.
    """
    will = df.copy()

    # Smoothing
    if smooth_params is not None:
        E_s = smooth(will["E"], smooth_params)
        S_s = smooth(will["S"], smooth_params)
        div_s = smooth(will["div"], smooth_params) if "div" in will else pd.Series(np.zeros(len(will)))
    else:
        E_s, S_s = will["E"], will["S"]
        div_s = will.get("div", pd.Series(np.zeros(len(will))))

    # Base terms
    A = zscore(E_s) * float(weights[0]) + zscore(S_s) * float(weights[1])

    # Optional derivative term from divergence proxy
    if include_derivatives and "div" in will:
        ddiv = diff_abs(div_s)
        A = A + zscore(ddiv) * float(weights[2])

    will[out_col] = A.astype("float64")
    return will
