#!/bin/bash
set -euo pipefail

echo "[oracle] Starting trafaret Oracle solution"

# Get the directory where this script is located
BUNDLE_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE_ARCHIVE="$BUNDLE_DIR/source.tar.gz"
EXPECTED_SHA256="d9d00800318fbd343fdfb3353e947b2ebb5557159c844696c5ac24846f76d41c"

if [ ! -f "$SOURCE_ARCHIVE" ]; then
    echo "[oracle] ERROR: Source archive not found at $SOURCE_ARCHIVE" >&2
    exit 1
fi

# Verify SHA-256
echo "[oracle] Verifying source archive integrity"
ACTUAL_SHA256=$(sha256sum "$SOURCE_ARCHIVE" | awk '{print $1}')

if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
    echo "[oracle] ERROR: SHA-256 mismatch" >&2
    echo "[oracle]   Expected: $EXPECTED_SHA256" >&2
    echo "[oracle]   Actual:   $ACTUAL_SHA256" >&2
    exit 1
fi

echo "[oracle] SHA-256 verified: $ACTUAL_SHA256"

# Extract to workspace
echo "[oracle] Extracting source to /workspace"
cd /workspace
tar -xzf "$SOURCE_ARCHIVE" --strip-components=1

# Verify we got the expected structure
if [ ! -f "setup.py" ]; then
    echo "[oracle] ERROR: setup.py not found after extraction" >&2
    exit 1
fi

if [ ! -d "trafaret" ]; then
    echo "[oracle] ERROR: trafaret directory not found after extraction" >&2
    exit 1
fi

echo "[oracle] Source extracted successfully"
echo "[oracle] Installing package"

# Install the package
pip install --no-cache-dir --no-build-isolation -e . || {
    echo "[oracle] ERROR: Installation failed" >&2
    exit 1
}

echo "[oracle] Installation complete"

# Verify import works
python -c "import trafaret; print(f'[oracle] trafaret version: {trafaret.__VERSION__}')" || {
    echo "[oracle] ERROR: Import verification failed" >&2
    exit 1
}

echo "[oracle] Oracle solution ready"
