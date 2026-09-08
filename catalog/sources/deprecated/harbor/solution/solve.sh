#!/bin/bash
set -euo pipefail

echo "[oracle] Starting deprecated Oracle solution"

# Locate the bundle directory
BUNDLE_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE_ARCHIVE="$BUNDLE_DIR/source-d135459ef6c1fdd005f28c6e2cf7915e8fb8d0e1.tar.gz"
EXPECTED_SHA256="823fb9443b01019b7b608f316882cdca0a4c86032eed207c76055cb368d864c6"

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

if [ ! -d "deprecated" ]; then
    echo "[oracle] ERROR: deprecated directory not found after extraction" >&2
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
echo "[oracle] Verifying installation"

# Verify import works
python3 -c "import deprecated; from deprecated import deprecated_params; from deprecated.sphinx import versionadded, versionchanged" || {
    echo "[oracle] ERROR: Import verification failed" >&2
    exit 1
}

echo "[oracle] Oracle solution ready"
