#!/usr/bin/env bash
set -euo pipefail

# Oracle solution for pycountry task.
# Extracts the frozen source archive bundled in this Oracle artifact and installs
# it into /workspace. NoNetwork: everything is read from the bundle.

EXPECTED_SHA256="5b6027d453fcd6060112b951dd010f01f168b51b4bf8a1f1fc8c95c8d94a0801"
echo "[oracle] Starting pycountry Oracle solution"

BUNDLE_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE_ARCHIVE="${BUNDLE_DIR}/pycountry-26.2.16.tar.gz"
WORKSPACE="/workspace"

if [ ! -f "$SOURCE_ARCHIVE" ]; then
    echo "[oracle] ERROR: Source archive not found at $SOURCE_ARCHIVE" >&2
    exit 1
fi

ACTUAL_SHA256=$(sha256sum "$SOURCE_ARCHIVE" | awk '{print $1}')
if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
    echo "[oracle] ERROR: Source SHA-256 mismatch" >&2
    echo "[oracle]   Expected: $EXPECTED_SHA256" >&2
    echo "[oracle]   Actual:   $ACTUAL_SHA256" >&2
    exit 1
fi
echo "[oracle] Source SHA-256 verified: $ACTUAL_SHA256"

# Extract source archive (topology: pycountry-26.2.16/ prefix) into /workspace
echo "[oracle] Extracting source to /workspace"
tar -xzf "$SOURCE_ARCHIVE" -C "$WORKSPACE" --strip-components=1

if [ ! -f "$WORKSPACE/pyproject.toml" ]; then
    echo "[oracle] ERROR: pyproject.toml not found after extraction" >&2
    exit 1
fi
if [ ! -d "$WORKSPACE/src/pycountry" ]; then
    echo "[oracle] ERROR: src/pycountry not found after extraction" >&2
    exit 1
fi

echo "[oracle] Installing pycountry with --no-build-isolation"
python -m pip install --no-build-isolation --no-deps --no-index -e "$WORKSPACE"

echo "[oracle] Verifying installation"
python3 -c "import pycountry; print('pycountry installed')"

echo "[oracle] Oracle solution installed successfully"
