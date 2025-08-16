[CmdletBinding()]
param(
  [ValidateSet("Debug","Release","RelWithDebInfo","MinSizeRel")]
  [string]$Config = "Release",
  [string]$Triplet = "x64-windows"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSCommandPath
$RepoRoot = Split-Path -Parent $RepoRoot  
Push-Location $RepoRoot

$VcpkgRoot = Join-Path $env:LOCALAPPDATA "vcpkg"
$Toolchain = Join-Path $VcpkgRoot "scripts\buildsystems\vcpkg.cmake"
if (-not (Test-Path $Toolchain)) {
  throw "vcpkg toolchain not found. Run tools/setup_vcpkg_windows.ps1 first."
}

$BuildDir = Join-Path "build" "$Triplet-$Config"
New-Item -ItemType Directory -Force -Path $BuildDir | Out-Null

cmake -S . -B $BuildDir `
  -DCMAKE_TOOLCHAIN_FILE="$Toolchain" `
  -DVCPKG_TARGET_TRIPLET="$Triplet" `
  -DCMAKE_BUILD_TYPE="$Config"

cmake --build $BuildDir --config $Config

$OutDir = Join-Path "python" "cdproc"
Write-Host "If build succeeded, the extension should be at: $OutDir"
Pop-Location
