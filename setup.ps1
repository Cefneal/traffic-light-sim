#!/usr/bin/env pwsh
# TLS - Traffic Light Simulation Setup (PowerShell)

$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptPath

Write-Host "=== TLS - Traffic Light Simulation Setup ===" -ForegroundColor Cyan
Write-Host ""

# ── Python check ────────────────────────────────
Write-Host "[1/4] Checking Python..." -ForegroundColor Yellow
try {
    $pyVersion = python --version 2>&1 | Select-Object -First 1
    Write-Host "  $pyVersion"
    if ($pyVersion -match "3\.14") {
        Write-Host "  WARNING: Python 3.14 may not have compatible wheels. Use 3.10-3.13." -ForegroundColor Red
    }
} catch {
    Write-Host "  ERROR: Python not found." -ForegroundColor Red
    Write-Host "  Install Python 3.10-3.13 from: https://www.python.org/downloads/"
    Write-Host "  Check 'Add Python to PATH' during installation."
    exit 1
}
Write-Host ""

# ── Virtual environment ─────────────────────────
Write-Host "[2/4] Setting up virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path "venv\Scripts\python.exe")) {
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ERROR: Failed to create virtual environment." -ForegroundColor Red
        exit 1
    }
    Write-Host "  Created venv/"
} else {
    Write-Host "  venv/ already exists"
}
Write-Host ""

# ── Activate & install ──────────────────────────
Write-Host "[3/4] Installing Python dependencies..." -ForegroundColor Yellow
$venvPython = Join-Path $PWD "venv\Scripts\python.exe"

& $venvPython -m pip install --upgrade pip -q
if ($LASTEXITCODE -ne 0) {
    Write-Host "  WARNING: pip upgrade failed, continuing..." -ForegroundColor Yellow
}

# Core deps - try PyQt6 first, fallback to PyQt5
& $venvPython -m pip install PyQt6 pyqtgraph traci -q
if ($LASTEXITCODE -ne 0) {
    Write-Host "  PyQt6 failed, trying PyQt5..." -ForegroundColor Yellow
    & $venvPython -m pip install PyQt5 pyqtgraph traci -q
}
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: Core dependencies failed to install." -ForegroundColor Red
    Write-Host "  Try: pip install PyQt6 pyqtgraph traci"
    exit 1
}

# WeasyPrint (optional)
& $venvPython -m pip install weasyprint -q
if ($LASTEXITCODE -ne 0) {
    Write-Host "  INFO: weasyprint skipped (optional, for PDF export)" -ForegroundColor Yellow
}

Write-Host "  Done."
Write-Host ""

# ── Check SUMO ──────────────────────────────────
Write-Host "[4/4] Checking SUMO..." -ForegroundColor Yellow
$sumoPaths = @(
    "sumo.exe",
    "C:\Program Files\SUMO\bin\sumo.exe",
    "C:\Program Files (x86)\SUMO\bin\sumo.exe",
    "$env:SUMO_HOME\bin\sumo.exe"
)
$found = $false
foreach ($p in $sumoPaths) {
    if (Test-Path $p) {
        Write-Host "  OK: SUMO found at $p" -ForegroundColor Green
        $found = $true
        break
    }
}
if ("sumo.exe" -in $sumoPaths -and -not $found) {
    try {
        $v = & "sumo.exe" --version 2>&1 | Select-Object -First 1
        if ($v) { Write-Host "  OK: $v" -ForegroundColor Green; $found = $true }
    } catch {}
}
if (-not $found) {
    Write-Host "  WARNING: SUMO not found in PATH." -ForegroundColor Yellow
    Write-Host "  Download from: https://sumo.dlr.de/docs/Downloads.php"
    Write-Host "  Or set SUMO_HOME env var to installation directory."
    Write-Host "  The app will not start without SUMO."
}
Write-Host ""

# ── Done ────────────────────────────────────────
Write-Host "=== Setup complete! ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Run the app:" -ForegroundColor Green
Write-Host "  .\venv\Scripts\Activate.ps1 ; python -m app.main"
Write-Host ""
