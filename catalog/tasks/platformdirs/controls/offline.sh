#!/bin/bash
set -euo pipefail

echo "[control:offline] Verifying offline verifier execution"
echo "[control:offline] This control reuses the Oracle solution and runs in no-network mode"
echo "[control:offline] The verifier will validate that public_network_available=false"

# Locate the bundle directory containing the Oracle source
BUNDLE_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE_ARCHIVE="$BUNDLE_DIR/../solution/source-frozen.tar.gz"

if [ ! -f "$SOURCE_ARCHIVE" ]; then
    echo "[control:offline] ERROR: Oracle source archive not found" >&2
    echo "[control:offline] Looking for: $SOURCE_ARCHIVE" >&2
    exit 1
fi

EXPECTED_SHA256="0dd96317307f068fd3c2cc34e7e0b80dbe97c01047c9cd93285e9afd1175415f"

echo "[control:offline] Verifying source archive integrity"
ACTUAL_SHA256=$(sha256sum "$SOURCE_ARCHIVE" | awk '{print $1}')

if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
    echo "[control:offline] ERROR: SHA-256 mismatch" >&2
    echo "[control:offline]   Expected: $EXPECTED_SHA256" >&2
    echo "[control:offline]   Actual:   $ACTUAL_SHA256" >&2
    exit 1
fi

echo "[control:offline] SHA-256 verified"

# Clear and extract to workspace
rm -rf /workspace/*
cd /workspace
tar -xzf "$SOURCE_ARCHIVE"

# Verify structure
if [ ! -f "pyproject.toml" ] || [ ! -d "src/platformdirs" ]; then
    echo "[control:offline] ERROR: Invalid source structure after extraction" >&2
    exit 1
fi

echo "[control:offline] Installing package"
pip install --no-cache-dir --no-build-isolation --no-deps -e . || {
    echo "[control:offline] ERROR: Installation failed" >&2
    exit 1
}

echo "[control:offline] Installation complete (network should be disabled during verification)"
