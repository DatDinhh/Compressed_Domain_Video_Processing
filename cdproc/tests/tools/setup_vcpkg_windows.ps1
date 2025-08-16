[CmdletBinding()]
param(
  [string]$Triplet = "x64-windows"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$VcpkgRoot = Join-Path $env:LOCALAPPDATA "vcpkg"
$VcpkgExe  = Join-Path $VcpkgRoot "vcpkg.exe"
$Toolchain = Join-Path $VcpkgRoot "scripts\buildsystems\vcpkg.cmake"

if (-not (Test-Path $VcpkgRoot)) {
  git clone https://github.com/microsoft/vcpkg $VcpkgRoot
}

if (-not (Test-Path $VcpkgExe)) {
  & (Join-Path $VcpkgRoot "bootstrap-vcpkg.bat")
}

& $VcpkgExe integrate install

Write-Host "Installing ports for $Triplet ..."
& $VcpkgExe install "ffmpeg[avcodec,avformat,avutil,swscale,swresample]:$Triplet"
& $VcpkgExe install "pybind11:$Triplet"

Write-Host "Done."
Write-Host "Toolchain: $Toolchain"
Write-Host "Remember to pass:"
Write-Host "  -DCMAKE_TOOLCHAIN_FILE=`"$Toolchain`" -DVCPKG_TARGET_TRIPLET=$Triplet"
