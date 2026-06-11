#!/usr/bin/env bash
# setup.sh — Auto-install dependencies + verify environment
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "=== TLS — Traffic Light Simulation Setup ==="
echo ""

# ── Python check ──────────────────────────────────────────────
echo "[1/4] Checking Python..."
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        PY_VER=$("$cmd" --version 2>&1 | grep -Po '\d+\.\d+')
        if awk "BEGIN {exit !($PY_VER >= 3.10)}"; then
            PYTHON="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "ERROR: Python 3.10+ not found. Install it first."
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "  Windows: https://www.python.org/downloads/"
    exit 1
fi
echo "  Found: $($PYTHON --version)"

# ── Virtual environment ───────────────────────────────────────
echo "[2/4] Setting up virtual environment..."
if [ ! -d "venv" ]; then
    $PYTHON -m venv venv
    echo "  Created venv/"
else
    echo "  venv/ already exists"
fi

source venv/bin/activate

# ── Install Python deps ───────────────────────────────────────
echo "[3/4] Installing Python dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "  Done."

# ── Check SUMO ────────────────────────────────────────────────
echo "[4/4] Checking SUMO..."
SUMO_BIN=""
for candidate in sumo /usr/bin/sumo /usr/local/bin/sumo; do
    if command -v "$candidate" &>/dev/null; then
        SUMO_BIN="$candidate"
        break
    fi
done

if [ -n "$SUMO_BIN" ]; then
    SUMO_VER=$("$SUMO_BIN" --version 2>&1 | head -1)
    echo "  Found: $SUMO_VER"
else
    echo "  SUMO not found. Attempting automatic install..."
    if command -v apt &>/dev/null; then
        sudo apt install sumo sumo-tools -y
        SUMO_BIN="$(command -v sumo || true)"
        if [ -n "$SUMO_BIN" ]; then
            echo "  SUMO installed successfully: $($SUMO_BIN --version 2>&1 | head -1)"
        else
            echo "  WARNING: Auto-install failed. Install manually:"
            echo "    sudo apt install sumo sumo-tools"
        fi
    else
        echo "  WARNING: SUMO not found. Install manually:"
        echo "    Ubuntu/Debian: sudo apt install sumo sumo-tools"
        echo "    Windows: https://sumo.dlr.de/docs/Downloads.php"
    fi
fi

# ── Optional: Build ──────────────────────────────────────────
if [ "${1:-}" = "--build" ]; then
    echo "[5/5] Building executable..."
    pip install pyinstaller -q
    pyinstaller tls.spec --clean -y
    echo "  Build complete! Executable at dist/tls"
fi

echo ""
echo "=== Setup complete! ==="
echo "Run: python -m app.main"
echo "Or:  source venv/bin/activate && python -m app.main"
echo "Build standalone: bash setup.sh --build"
