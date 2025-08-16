from __future__ import annotations

import sys
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PKG_ROOT = REPO_ROOT / "python"
if str(PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(PKG_ROOT))


def _import_cdproc_cpp():
    try:
        from cdproc import cdproc_cpp 
        return cdproc_cpp
    except Exception:
        try:
            import cdproc_cpp  
            return cdproc_cpp
        except Exception as e:
            pytest.skip(f"cdproc_cpp not importable yet: {e!r}")


def test_module_import_and_api():
    mod = _import_cdproc_cpp()
    assert hasattr(mod, "extract_features"), "cdproc_cpp.extract_features is missing"
    assert callable(mod.extract_features), "extract_features should be callable"


def test_extract_raises_on_missing_file(tmp_path: Path):
    mod = _import_cdproc_cpp()
    # Use a definitely-nonexistent path
    bad = tmp_path / "does_not_exist.mp4"
    with pytest.raises(Exception):
        mod.extract_features(str(bad))


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg not found on PATH")
def test_extract_on_tiny_clip_if_possible(tmp_path: Path):
    """
    Optional smoke: if ffmpeg is present, synthesize a 1.5s clip with a moving square,
    then call the extractor and ensure we receive a list of per-frame dicts.
    """
    mod = _import_cdproc_cpp()

    # Prefer an existing small clip under data/, otherwise synthesize
    clip = REPO_ROOT / "data" / "synth_square.mp4"
    if not clip.exists():
        clip.parent.mkdir(parents=True, exist_ok=True)
        ffmpeg = shutil.which("ffmpeg")

        # Escaped comma in the mod() argument: 40\,120
        filtergraph = "drawbox=x=mod(t*40\\,120):y=45:w=30:h=30:color=white@1.0:t=fill,format=yuv420p"
        cmd = [
            ffmpeg,
            "-v", "error",
            "-y",
            "-f", "lavfi", "-i", "color=black:s=160x120:r=30",
            "-vf", filtergraph,
            "-t", "1.5",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
            "-g", "48", "-bf", "2",
            str(clip),
        ]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if proc.returncode != 0:
            pytest.skip(f"ffmpeg synthesis failed: {proc.stderr[-400:]}")

    rows = mod.extract_features(str(clip))
    assert isinstance(rows, list), "extract_features should return a list"
    assert len(rows) >= 10, f"unexpectedly few frames: {len(rows)}"
    sample = rows[0]
    assert isinstance(sample, dict), "each row should be a dict"
    for key in ("t", "E", "S", "div"):
        assert key in sample, f"missing key '{key}' in feature row"
