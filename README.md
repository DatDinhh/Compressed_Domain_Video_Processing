# Compressed-Domain Video Processing
This project explores **video analysis directly in the compressed domain**. Instead of fully decoding every frame, we leverage **motion vectors and side-data** embedded in codecs like H.264 to perform tasks such as:
- Shot Boundary Detection – automatically detect scene cuts
- Actionness Scoring – measure motion intensity to locate highlights
- Motion Visualization – render motion vectors overlaid on video
- Efficient Feature Extraction – extract per-frame motion features without full decode

## Why Compressed-Domain Processing?
Traditional pipelines decode video into raw RGB before analysis, which is:
- Slow (high compute cost)
- Memory-heavy (raw frames consume lots of RAM/storage)
By staying in the **compressed domain**, we directly reuse information the codec already computed (motion vectors, macroblocks, residuals). This makes analysis faster, lighter, and scalable.

## Project Structure
cdproc/
├── cpp/                # C++ backend (feature extraction, bindings)
├── python/             # Python package + scripts
│   ├── cdproc/         # IO + utilities
│   └── scripts/        # CLI scripts (extract, detect, score)
├── tests/              # Synthetic clip generator, unit tests
└── data/               # Sample video data (not included in repo)

## Quickstart
### 1. Build
git clone https://github.com/microsoft/vcpkg $env:LOCALAPPDATA\vcpkg
& "$env:LOCALAPPDATA\vcpkg\bootstrap-vcpkg.bat"
& "$env:LOCALAPPDATA\vcpkg\vcpkg.exe" install ffmpeg:x64-windows
cmake -S . -B build -G "Visual Studio 17 2022" -A x64 `
  -DCMAKE_TOOLCHAIN_FILE="$env:LOCALAPPDATA\vcpkg\scripts\buildsystems\vcpkg.cmake" `
  -DVCPKG_TARGET_TRIPLET=x64-windows
cmake --build build --config Release

### 2. Activate Python
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

### 3. Run Pipeline
python .\python\scripts\extract_features.py --video data\video_h264.mp4 --out features.csv
python .\python\scripts\detect_shots.py --features features.csv --out shots.csv
python .\python\scripts\score_actionness.py --features features.csv --timeline timeline.png

### 4. Export Highlights
.\tools\export_shots.ps1 -ShotsCsv shots.csv -Video data\video_h264.mp4 -OutDir highlights

### 5. Visualize Motion Vectors
ffmpeg -flags2 +export_mvs -i data\video_h264.mp4 `
  -vf "codecview=mv=pf+bf+bb:qp=1" `
  out\video_with_mvs.mp4

## Example Outputs
- features.csv → per-frame motion metrics (E, S, divergence)
- shots.csv → detected shot boundaries
- timeline.png → activity plot across the video
- highlights/ → auto-extracted highlight clips
- video_with_mvs.mp4 → original video with motion vectors overlaid

## Future Work
- Support for more codecs (HEVC, AV1)
- ML models trained directly on compressed-domain features
- Real-time streaming integration (live sports, surveillance)

## License
MIT License. See LICENSE for details.

## Acknowledgements
- FFmpeg for motion vector extraction
- pybind11 for Python bindings
- vcpkg for package management
