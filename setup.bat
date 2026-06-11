@echo off
chcp 65001 >nul
title TLS - Traffic Light Simulation Setup

echo === TLS - Traffic Light Simulation Setup ===
echo.

REM ── Python check ────────────────────────────────
echo [1/4] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Install Python 3.10+ from:
    echo   https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
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
