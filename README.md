# Compressed-Domain Video Processing (cdproc)

Compressed-Domain Video Processing (“cdproc”) is a toolkit that analyzes video directly in the compressed domain by extracting features from codec motion vectors, without decoding full RGB frames. This makes it lightweight, fast, and scalable for video analytics tasks like shot detection and highlight extraction.

Features:
- Extract motion-vector features directly from compressed video streams
- Detect shot boundaries from motion patterns
- Score actionness over time and visualize results
- Export highlights around detected cuts
- Visualize motion vectors with FFmpeg codecview

Repository Layout:
- cpp/ — C++ sources for motion vector extraction and Python bindings
- python/ — Python package and analysis scripts
- tests/ — synthetic clip generator and smoke tests
- tools/ — helper scripts for building and exporting
- data/ — sample videos

Quickstart (Windows, PowerShell):

git clone https://github.com/DatDinhh/Compressed_Domain_Video_Processing.git C:\cdproc
cd C:\cdproc
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install pybind11 pandas matplotlib pytest

git clone https://github.com/microsoft/vcpkg $env:LOCALAPPDATA\vcpkg
& $env:LOCALAPPDATA\vcpkg\bootstrap-vcpkg.bat
& $env:LOCALAPPDATA\vcpkg\vcpkg.exe install ffmpeg[avcodec,avformat,avutil,swscale,swresample]:x64-windows

cmake -S . -B build -G "Visual Studio 17 2022" -A x64 `
  -DCMAKE_BUILD_TYPE=Release `
  -DCMAKE_TOOLCHAIN_FILE="$env:LOCALAPPDATA\vcpkg\scripts\buildsystems\vcpkg.cmake" `
  -DVCPKG_TARGET_TRIPLET=x64-windows `
  -Dpybind11_DIR="$(python -c "import pybind11, pathlib; print(pathlib.Path(pybind11.get_cmake_dir()))")"

cmake --build build --config Release

Usage:

python .\python\scripts\extract_features.py --video .\data\video.mp4 --out features.csv
python .\python\scripts\detect_shots.py --features features.csv --out shots.csv
python .\python\scripts\score_actionness.py --features features.csv --timeline timeline.png
.\tools\export_shots.ps1 -ShotsCsv shots.csv -Video .\data\video.mp4 -OutDir .\highlights
ffmpeg -flags2 +export_mvs -i .\data\video.mp4 -vf "codecview=mv=pf+bf+bb:qp=1" out_with_mvs.mp4

License: MIT
