#!/usr/bin/env bash
# setup.sh — Auto-install dependencies + verify environment (Linux / macOS)
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
        PY_VER=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
        MAJOR=$(echo "$PY_VER" | cut -d. -f1)
        MINOR=$(echo "$PY_VER" | cut -d. -f2)
        if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 10 ] 2>/dev/null; then
            PYTHON="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "ERROR: Python 3.10+ not found. Install it first."
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "  macOS: brew install python"
    echo "  Windows: https://www.python.org/downloads/"
    exit 1
fi
PY_FULL=$($PYTHON --version 2>&1)
echo "  Found: $PY_FULL"
if echo "$PY_FULL" | grep -q "3\.14"; then
    echo "  WARNING: Python 3.14 may lack wheels for some packages." >&2
    echo "  Consider Python 3.10-3.13 if installs fail." >&2
fi

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
pip install --upgrade pip -q 2>/dev/null || true

# Core deps — try PyQt6 first, fall back to PyQt5
set +e
if pip install "PyQt6>=6.5" -q 2>/dev/null; then
    echo "  Installed PyQt6 (GUI framework)"
elif pip install "PyQt5>=5.15" -q 2>/dev/null; then
    echo "  Installed PyQt5 (GUI framework, macOS <13 fallback)"
else
    echo "ERROR: Could not install PyQt5 or PyQt6."
    echo "  Try: pip install PyQt5 pyqtgraph traci --only-binary :all:"
    exit 1
fi
pip install pyqtgraph traci -q 2>/dev/null
set -e

# WeasyPrint (optional)
pip install weasyprint -q 2>/dev/null || echo "  INFO: weasyprint skipped (optional, PDF export)"

echo "  Done."

# ── Check SUMO ────────────────────────────────────────────────
echo "[4/4] Checking SUMO..."
SUMO_BIN=""
for candidate in sumo /usr/bin/sumo /usr/local/bin/sumo /opt/homebrew/bin/sumo; do
    if command -v "$candidate" &>/dev/null; then
        SUMO_BIN="$candidate"
        break
    fi
done

if [ -n "$SUMO_BIN" ]; then
    SUMO_VER=$("$SUMO_BIN" --version 2>&1 | head -1)
    echo "  Found: $SUMO_VER"
else
    # Check pip-installed eclipse-sumo
    if python3 -c "import eclipse_sumo; print(eclipse_sumo.__file__)" 2>/dev/null; then
        ESM=$(python3 -c "import eclipse_sumo; import os; print(os.path.dirname(eclipse_sumo.__file__))" 2>/dev/null)
        if [ -x "$ESM/bin/sumo" ]; then
            SUMO_BIN="$ESM/bin/sumo"
            echo "  Found (pip): $($SUMO_BIN --version 2>&1 | head -1)"
        else
            echo "  WARNING: eclipse-sumo installed via pip but binary not found at $ESM/bin/sumo" >&2
        fi
    else
        echo "  SUMO not found. Attempting install..."
        if command -v apt &>/dev/null; then
            sudo apt install sumo sumo-tools -y
            SUMO_BIN="$(command -v sumo || true)"
        elif command -v brew &>/dev/null; then
            brew install sumo
            SUMO_BIN="$(command -v sumo || true)"
        fi
        if [ -n "$SUMO_BIN" ]; then
            echo "  Installed: $($SUMO_BIN --version 2>&1 | head -1)"
        else
            echo "  WARNING: SUMO not found. Try: pip install eclipse-sumo"
            echo "    Or download from: https://sumo.dlr.de/docs/Downloads.php"
        fi
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
