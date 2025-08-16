import sys
import subprocess
import shutil
from pathlib import Path

import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PKG_ROOT = REPO_ROOT / "python"
if str(PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(PKG_ROOT))

try:
    from cdproc import extract_features 
    from cdproc.io import write_features_csv, load_features
    from cdproc.detect import detect_shots, TwoThreshParams
    from cdproc.features import compute_actionness, SmoothParams
    from cdproc.plot import plot_timeline
except Exception as e:
    pytest.skip(f"cdproc package not importable yet: {e}", allow_module_level=True)

FFMPEG = shutil.which("ffmpeg")


@pytest.mark.skipif(FFMPEG is None, reason="ffmpeg not found on PATH")
def test_full_pipeline_on_synth_clip(tmp_path: Path):
    """Synthesize a clip, run extractor → CSV → detect → score → plot."""
    out_mp4 = tmp_path / "synth_square.mp4"

    filtergraph = "drawbox=x=mod(t*40\\,120):y=45:w=30:h=30:color=white@1.0:t=fill,format=yuv420p"
    cmd = [
        FFMPEG, "-y",
        "-f", "lavfi", "-i", "color=black:s=160x120:r=30",
        "-vf", filtergraph,
        "-t", "3",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        "-g", "48", "-bf", "2",
        str(out_mp4),
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert proc.returncode == 0, f"ffmpeg synthesis failed: {proc.stderr[-500:]}"

    rows = extract_features(str(out_mp4))
    assert isinstance(rows, list) and len(rows) >= 10, "no frames extracted"

    df = pd.DataFrame(rows)
    assert df["E"].sum() > 0 or df["S"].sum() > 0, "E/S appear all zero; check decoder/flags"

    feat_csv = tmp_path / "features.csv"
    write_features_csv(rows, feat_csv)
    df2 = load_features(feat_csv)
    assert len(df2) == len(df) and {"E", "S", "div"}.issubset(df2.columns)

    shots = detect_shots(df2, TwoThreshParams())
    assert {"frame", "t"}.issubset(shots.columns)

    df3 = compute_actionness(df2, SmoothParams(kind="ema", window=5))
    png = tmp_path / "timeline.png"
    plot_timeline(df3, out_path=png, metric="actionness", shots=shots, title="Actionness")
    assert png.exists() and png.stat().st_size > 0
