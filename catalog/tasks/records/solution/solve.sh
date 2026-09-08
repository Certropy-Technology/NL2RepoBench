#!/bin/bash
set -euo pipefail

echo "[oracle] Starting records Oracle solution"

# Locate the bundle directory
BUNDLE_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE_ARCHIVE="$BUNDLE_DIR/source-frozen.tar.gz"
EXPECTED_SHA256="3c13f1ba614bb512e566203d76cfc2ed2225fd021832ad875e87bf017cbeeea4"

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

# Clean workspace and extract
echo "[oracle] Cleaning workspace and extracting source to /workspace"
rm -rf /workspace/*
cd /workspace
tar -xzf "$SOURCE_ARCHIVE" --strip-components=1

# Verify extracted structure
if [ ! -f "setup.py" ]; then
    echo "[oracle] ERROR: setup.py not found after extraction" >&2
    exit 1
fi

if [ ! -f "records.py" ]; then
    echo "[oracle] ERROR: records.py not found after extraction" >&2
    exit 1
fi

echo "[oracle] Source extracted successfully"
echo "[oracle] Installing package"

# Install the package with no build isolation
pip install --no-cache-dir --no-build-isolation -e . || {
    echo "[oracle] ERROR: Installation failed" >&2
    exit 1
}

# Verify installation
python -c "import records; print('[oracle] records imported successfully')" || {
    echo "[oracle] ERROR: Failed to import records" >&2
    exit 1
}

echo "[oracle] Installation complete"
echo "[oracle] Oracle solution ready"
