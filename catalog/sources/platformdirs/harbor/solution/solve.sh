#!/bin/bash
set -euo pipefail

echo "[oracle] Starting platformdirs Oracle solution"

# Locate the bundle directory
BUNDLE_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE_ARCHIVE="$BUNDLE_DIR/source-frozen.tar.gz"
EXPECTED_SHA256="995328414976fd680723de17b111b8024272ed80d558609fe80d7f48253d80b2"

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

# Clear and extract to workspace
echo "[oracle] Extracting source to /workspace"
rm -rf /workspace/*
cd /workspace
tar -xzf "$SOURCE_ARCHIVE"

# Verify structure
if [ ! -f "pyproject.toml" ]; then
    echo "[oracle] ERROR: pyproject.toml not found after extraction" >&2
    exit 1
fi

if [ ! -d "src/platformdirs" ]; then
    echo "[oracle] ERROR: src/platformdirs directory not found after extraction" >&2
    exit 1
fi

if [ ! -f "src/platformdirs/version.py" ]; then
    echo "[oracle] ERROR: src/platformdirs/version.py not found after extraction" >&2
    exit 1
fi

echo "[oracle] Source extracted successfully"
echo "[oracle] Installing package"

# Install the package with --no-build-isolation since we have hatchling in the environment
pip install --no-cache-dir --no-build-isolation --no-deps . || {
    echo "[oracle] ERROR: Installation failed" >&2
    exit 1
}

echo "[oracle] Verifying installation"
python -c "import platformdirs; print(f'platformdirs version: {platformdirs.__version__}')" || {
    echo "[oracle] ERROR: Import verification failed" >&2
    exit 1
}

echo "[oracle] Installation complete"
echo "[oracle] Oracle solution ready"
