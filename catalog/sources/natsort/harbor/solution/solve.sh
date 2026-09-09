#!/bin/bash
set -euo pipefail

echo "[oracle] Starting natsort Oracle solution"

# Verify we have the source archive
SOURCE_ARCHIVE="/solution/source.tar.gz"
EXPECTED_SHA256="45312c4a0e5507593da193dedd04abb1469253b601ecaf63445ad80f0a1ea581"

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
if [ ! -f "setup.py" ] && [ ! -f "pyproject.toml" ]; then
    echo "[oracle] ERROR: Neither setup.py nor pyproject.toml found after extraction" >&2
    exit 1
fi

if [ ! -d "natsort" ]; then
    echo "[oracle] ERROR: natsort directory not found after extraction" >&2
    exit 1
fi

echo "[oracle] Source extracted successfully"
echo "[oracle] Installing package"

# Install the package
pip install --no-cache-dir --no-build-isolation --no-index -e . || {
    echo "[oracle] ERROR: Installation failed" >&2
    exit 1
}

echo "[oracle] Installation complete"

# Verify import works
python3 -c "import natsort; print(f'[oracle] natsort version: {natsort.__version__}')" || {
    echo "[oracle] ERROR: Cannot import natsort" >&2
    exit 1
}

echo "[oracle] Oracle solution ready"
