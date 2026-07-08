$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

$Python = if ($env:PYTHON) { $env:PYTHON } else { "python" }

Write-Host "RuleBridge Windows build (delegating to build.py)..." -ForegroundColor Cyan
& $Python build.py --platform win @args
if ($LASTEXITCODE -ne 0) {
    throw "build.py failed with exit code $LASTEXITCODE"
}
