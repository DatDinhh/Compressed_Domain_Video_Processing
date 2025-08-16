from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import pandas as pd


FEATURE_DTYPES = {"t": "float64", "E": "float64", "S": "float64", "div": "float64"}
SHOT_DTYPES = {"t": "float64", "frame": "int64", "score": "float64", "rule": "string"}


def _ensure_parent(path: str | os.PathLike) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def write_features_csv(rows: Iterable[Mapping[str, float]], out_csv: str | os.PathLike) -> None:
    """
    Write feature rows (t/E/S/div) to CSV with stable dtypes and header.
    """
    _ensure_parent(out_csv)
    df = pd.DataFrame(rows, columns=["t", "E", "S", "div"]).astype(FEATURE_DTYPES)
    df.to_csv(out_csv, index=False)


def load_features(csv_path: str | os.PathLike) -> pd.DataFrame:
    """
    Load features CSV into a DataFrame with strong dtypes.
    """
    df = pd.read_csv(csv_path, dtype=FEATURE_DTYPES)
    # Ensure time is monotonic if it's present; if not, synthesize frame index
    if "t" in df.columns and not df["t"].is_monotonic_increasing:
        df = df.sort_values("t", kind="mergesort").reset_index(drop=True)
    if "frame" not in df.columns:
        df.insert(0, "frame", range(len(df)))
    return df


def write_shots_csv(df_shots: pd.DataFrame, out_csv: str | os.PathLike) -> None:
    """
    Persist shots dataframe (frame/t/score/rule) to CSV.
    """
    _ensure_parent(out_csv)
    cols = ["frame", "t", "score", "rule"]
    for c in cols:
        if c not in df_shots.columns:
            raise ValueError(f"shots DataFrame missing column: {c}")
    df_shots[cols].astype({"frame": "int64", "t": "float64", "score": "float64", "rule": "string"}).to_csv(
        out_csv, index=False
    )


def load_shots(csv_path: str | os.PathLike) -> pd.DataFrame:
    return pd.read_csv(csv_path, dtype=SHOT_DTYPES)


def describe_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a numeric summary for quick sanity checks.
    """
    cols = [c for c in ["E", "S", "div"] if c in df.columns]
    return df[cols].describe()
