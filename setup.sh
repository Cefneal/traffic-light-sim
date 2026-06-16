#!/usr/bin/env bash
# setup.sh — Auto-install dependencies + verify environment (Linux / macOS / WSL)
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

OS="$(uname -s)"
echo "=== TLS — Traffic Light Simulation Setup ==="
echo "  OS: $OS"
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
    echo "ERROR: Python 3.10+ not found."
    echo "  Arch:        sudo pacman -S python python-pip python-virtualenv"
    echo "  Ubuntu/Deb:  sudo apt install python3 python3-pip python3-venv"
    echo "  macOS:       brew install python"
    echo "  Windows:     https://www.python.org/downloads/"
    exit 1
fi
PY_FULL=$($PYTHON --version 2>&1)
echo "  Found: $PY_FULL"
PY_MINOR=$(echo "$PY_FULL" | sed 's/.* \([0-9]*\)\.\([0-9]*\)\..*/\2/')
if [ "$PY_MINOR" -ge 14 ] 2>/dev/null; then
    echo "  WARNING: Python 3.14+ may lack PyQt wheels. Install Python 3.12 if installs fail." >&2
fi

# ── Virtual environment ───────────────────────────────────────
echo "[2/4] Setting up virtual environment..."
if [ ! -d "venv" ]; then
    $PYTHON -m venv venv
    echo "  Created venv/"
else
    echo "  venv/ already exists"
fi

# shellcheck disable=SC1091
source venv/bin/activate

# ── Install Python deps ───────────────────────────────────────
echo "[3/4] Installing Python dependencies..."
pip install --upgrade pip -q 2>/dev/null || true

MACOS_VER=""
if [ "$OS" = "Darwin" ]; then
    MACOS_VER=$(sw_vers -productVersion 2>/dev/null | cut -d. -f1)
fi

set +e
if [ -n "$MACOS_VER" ] && [ "$MACOS_VER" -lt 13 ] 2>/dev/null; then
    echo "  macOS $MACOS_VER detected — PyQt6 requires macOS 13+, using PyQt5"
    if pip install "PyQt5>=5.15" -q 2>/dev/null; then
        echo "  Installed PyQt5 (GUI framework)"
    else
        echo "ERROR: PyQt5 installation failed. Try: pip install PyQt5 --only-binary :all:"
        exit 1
    fi
elif pip install "PyQt6>=6.5" -q 2>/dev/null; then
    echo "  Installed PyQt6 (GUI framework)"
elif pip install "PyQt5>=5.15" -q 2>/dev/null; then
    echo "  Installed PyQt5 (GUI framework)"
else
    echo "ERROR: Could not install PyQt5 or PyQt6."
    echo "  Arch:        sudo pacman -S python-pyqt5 python-pyqtgraph"
    echo "  Ubuntu/Deb:  sudo apt install python3-pyqt5 python3-pyqtgraph"
    echo "  macOS:       brew install pyqt5"
    exit 1
fi
pip install pyqtgraph traci -q 2>/dev/null
set -e

pip install weasyprint -q 2>/dev/null || echo "  INFO: weasyprint skipped (optional, PDF export)"

echo "  Done."

# ── Check SUMO ────────────────────────────────────────────────
echo "[4/4] Checking SUMO..."
SUMO_BIN=""

# 1. Check PATH
if command -v sumo &>/dev/null; then
    SUMO_BIN="$(command -v sumo)"
fi

# 2. Check common install locations
if [ -z "$SUMO_BIN" ]; then
    # macOS: built from source / Applications
    if [ "$OS" = "Darwin" ]; then
        for p in /Applications/SUMO/bin/sumo /usr/local/bin/sumo; do
            if [ -x "$p" ]; then
                SUMO_BIN="$p"
                SUMO_HOME="$(cd "$(dirname "$p")/.." && pwd)"
                export SUMO_HOME
                break
            fi
        done
    fi
fi

# 3. Check pip-installed eclipse-sumo (imports as `sumo`, not `eclipse_sumo`)
if [ -z "$SUMO_BIN" ]; then
    SUMO_DIR=$(python3 -c "import sumo; import os; print(os.path.dirname(sumo.__file__))" 2>/dev/null || true)
    if [ -n "$SUMO_DIR" ] && [ -x "$SUMO_DIR/bin/sumo" ]; then
        SUMO_BIN="$SUMO_DIR/bin/sumo"
        SUMO_HOME="$SUMO_DIR"
        export SUMO_HOME
        echo "  Found (pip eclipse-sumo): $("$SUMO_BIN" --version 2>&1 | head -1)"
    fi
fi

# 4. Try to install if missing
if [ -z "$SUMO_BIN" ]; then
    echo "  SUMO not found. Attempting install..."

    if command -v pacman &>/dev/null; then
        # Arch Linux
        if sudo pacman -S --noconfirm sumo sumo-tools 2>/dev/null; then
            SUMO_BIN="$(command -v sumo || true)"
        fi
    elif command -v apt &>/dev/null; then
        # Debian / Ubuntu
        sudo apt install sumo sumo-tools -y 2>/dev/null
        SUMO_BIN="$(command -v sumo || true)"
    fi

    # Fallback: pip install eclipse-sumo (all platforms)
    if [ -z "$SUMO_BIN" ]; then
        echo "  Installing eclipse-sumo via pip (includes SUMO binaries)..."
        pip install eclipse-sumo -q 2>/dev/null || true
        SUMO_DIR=$(python3 -c "import sumo; import os; print(os.path.dirname(sumo.__file__))" 2>/dev/null || true)
        if [ -n "$SUMO_DIR" ] && [ -x "$SUMO_DIR/bin/sumo" ]; then
            SUMO_BIN="$SUMO_DIR/bin/sumo"
            SUMO_HOME="$SUMO_DIR"
            export SUMO_HOME
        fi
    fi

    if [ -n "$SUMO_BIN" ]; then
        echo "  Installed: $("$SUMO_BIN" --version 2>&1 | head -1)"
    else
        echo "  WARNING: SUMO installation failed."
        echo "    Arch:        sudo pacman -S sumo sumo-tools"
        echo "    Ubuntu/Deb:  sudo apt install sumo sumo-tools"
        echo "    macOS:       brew tap dlr-ts/sumo && brew install sumo  OR  download from https://sumo.dlr.de"
        echo "    Windows:     pip install eclipse-sumo  OR  download from https://sumo.dlr.de"
        echo "    Or download: https://sumo.dlr.de/docs/Downloads.php"
    fi
fi

# ── Set SUMO_HOME if found but not set ─────────────────────────
if [ -n "$SUMO_BIN" ] && [ -z "${SUMO_HOME:-}" ]; then
    # Derive SUMO_HOME from binary path (bin/sumo -> parent dir)
    SUMO_HOME="$(cd "$(dirname "$SUMO_BIN")/.." && pwd)"
    export SUMO_HOME
fi
echo "  SUMO_HOME=${SUMO_HOME:-}"

# ── Optional: Build ──────────────────────────────────────────
if [ "${1:-}" = "--build" ]; then
    echo "[5/5] Building executable..."
    pip install pyinstaller -q
    pyinstaller tls.spec --clean -y
    echo "  Build complete! Executable at dist/tls"
fi

echo ""
echo "=== Setup complete! ==="
echo "Run:  source venv/bin/activate && python -m app.main"
echo "Fish: source venv/bin/activate.fish && python -m app.main"
echo "Build: bash setup.sh --build"
