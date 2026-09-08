#!/bin/bash
set -euo pipefail

echo "[oracle] Starting dpath Oracle solution"

# Verify we have the source archive
SOURCE_ARCHIVE="/solution/source.tar.gz"
EXPECTED_SHA256="a5c81f592150e8d3122f9567d09e436fca093c41b41ab88742f44942eb15fc0a"

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

if [ ! -d "dpath" ]; then
    echo "[oracle] ERROR: dpath directory not found after extraction" >&2
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

# Verify the package can be imported
python3 -c "import dpath; print(f'dpath version: {dpath.version.VERSION}')" || {
    echo "[oracle] ERROR: Import verification failed" >&2
    exit 1
}

echo "[oracle] Oracle solution ready"
