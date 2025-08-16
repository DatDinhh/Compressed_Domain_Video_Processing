from __future__ import annotations

__all__ = [
    "extract_features",
    "cdproc_cpp",
]

__version__ = "0.1.0"

try:
    from . import cdproc_cpp  
except Exception:  
    import cdproc_cpp 

def extract_features(video_path: str):
    """
    Extract per-frame compressed-domain features from `video_path`.

    Returns: list of dicts with keys: t, E, S, div
    """
    try:
        from . import cdproc_cpp as _cpp  
        return _cpp.extract_features(video_path)
    except Exception:
        import cdproc_cpp as _cpp  
        return _cpp.extract_features(video_path)
