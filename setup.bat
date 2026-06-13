@echo off
chcp 65001 >nul 2>&1
title TLS - Traffic Light Simulation Setup

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo === TLS - Traffic Light Simulation Setup ===
echo.

REM ── Python check ────────────────────────────────
echo [1/4] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   ERROR: Python not found.
    echo   Install Python 3.10 - 3.13 from:
    echo     https://www.python.org/downloads/
    echo   Check "Add Python to PATH" during installation.
    echo.
    echo   NOTE: Python 3.14 is NOT supported ^(libraries not ready^).
    pause
    exit /b 1
)
python --version
echo.

REM ── Virtual environment ─────────────────────────
echo [2/4] Setting up virtual environment...
if not exist venv\Scripts\python.exe (
    python -m venv venv
    if !errorlevel! neq 0 (
        echo   ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo   Created venv/
) else (
    echo   venv/ already exists
)
echo.

REM ── Install deps ────────────────────────────────
echo [3/4] Installing Python dependencies...
call venv\Scripts\activate.bat

python -m pip install --upgrade pip -q
if !errorlevel! neq 0 (
    echo   WARNING: pip upgrade failed, continuing...
)

REM Try core deps first (skip optional weasyprint on Windows)
pip install PyQt6 pyqtgraph traci -q
if !errorlevel! neq 0 (
    echo   ERROR: Core dependencies failed to install.
    echo   Try: pip install PyQt6 pyqtgraph traci
    pause
    exit /b 1
)

REM Try weasyprint (optional - for export)
pip install weasyprint -q
if !errorlevel! neq 0 (
    echo   INFO: weasyprint skipped ^(optional, for PDF export^)
)

echo   Done.
echo.

REM ── Check SUMO ──────────────────────────────────
echo [4/4] Checking SUMO...
where sumo >nul 2>&1
if %errorlevel% equ 0 (
    sumo --version
    echo   OK: SUMO found in PATH.
) else if exist "C:\Program Files\SUMO\bin\sumo.exe" (
    echo   OK: SUMO found at C:\Program Files\SUMO\bin\
) else if exist "C:\Program Files (x86)\SUMO\bin\sumo.exe" (
    echo   OK: SUMO found at C:\Program Files (x86)\SUMO\bin\
) else (
    echo   WARNING: SUMO not found.
    echo   Download from: https://sumo.dlr.de/docs/Downloads.php
    echo   Install to default location, or add bin/ to PATH.
    echo   The app will not start without SUMO.
)
echo.

echo === Setup complete! ===
echo.
echo Quick start:
echo   venv\Scripts\activate ^&^& python -m app.main
echo.
echo Or in PowerShell:
echo   venv\Scripts\Activate.ps1 ; python -m app.main
echo.
pause
    exit /b 1
)
python --version
echo.

REM ── Virtual environment ─────────────────────────
echo [2/4] Setting up virtual environment...
if not exist venv (
    python -m venv venv
    echo   Created venv/
) else (
    echo   venv/ already exists
)
echo.

REM ── Install deps ────────────────────────────────
echo [3/4] Installing Python dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip -q
pip install -r requirements.txt -q
echo   Done.
echo.

REM ── Check SUMO ──────────────────────────────────
echo [4/4] Checking SUMO...
where sumo >nul 2>&1
if %errorlevel% equ 0 (
    sumo --version
) else (
    echo   WARNING: SUMO not found in PATH.
    echo   Download from: https://sumo.dlr.de/docs/Downloads.php
    echo   After installing, set path via: File ^> Settings
)
echo.

echo === Setup complete! ===
echo.
echo Run: python -m app.main
echo Or:  venv\Scripts\activate ^&^& python -m app.main
echo.

pause
