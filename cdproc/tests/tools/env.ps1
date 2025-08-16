$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $PSCommandPath
$RepoRoot = Split-Path -Parent $Here

$Venv = Join-Path $RepoRoot ".venv"
$Act  = Join-Path $Venv "Scripts\Activate.ps1"
if (Test-Path $Act) {
  . $Act
  Write-Host "(venv) activated from $Venv"
} else {
  Write-Warning "No .venv found. Create one with: python -m venv .venv ; .\.venv\Scripts\Activate ; pip install -e ."
}

$VcpkgBin = Join-Path $env:LOCALAPPDATA "vcpkg\installed\x64-windows\bin"
if (Test-Path $VcpkgBin) {
  if ($env:Path -notlike "*$VcpkgBin*") {
    $env:Path = "$VcpkgBin;$env:Path"
    Write-Host "Prepended vcpkg bin to PATH: $VcpkgBin"
  }
} else {
  Write-Warning "vcpkg runtime bin not found. If FFmpeg DLLs fail to load, run tools/setup_vcpkg_windows.ps1"
}

$PkgRoot = Join-Path $RepoRoot "python"
if ($env:PYTHONPATH -notlike "*$PkgRoot*") {
  $env:PYTHONPATH = "$PkgRoot;$env:PYTHONPATH"
  Write-Host "Added to PYTHONPATH: $PkgRoot"
}

Write-Host "Environment ready."
