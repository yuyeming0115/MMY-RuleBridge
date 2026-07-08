$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Spec = Join-Path $Root "rulebridge.spec"
$DistExe = Join-Path $Root "dist\rulebridge.exe"
$Python = if ($env:PYTHON) { $env:PYTHON } else { "python" }

Set-Location $Root

Write-Host "Using Python:" -ForegroundColor Cyan
& $Python --version

Write-Host "Installing build dependencies..." -ForegroundColor Cyan
& $Python -m pip install --upgrade pyinstaller "pydantic>=2.0" "PyYAML>=6.0"

Write-Host "Building RuleBridge.exe..." -ForegroundColor Cyan
& $Python -m PyInstaller --noconfirm --clean $Spec

if (-not (Test-Path $DistExe)) {
    throw "Build failed: $DistExe not found."
}

Write-Host "Smoke testing executable..." -ForegroundColor Cyan
& $DistExe --help | Out-Host
& $DistExe list-targets | Out-Host

Write-Host "Built: $DistExe" -ForegroundColor Green
