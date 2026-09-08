#!/bin/bash
set -euo pipefail

echo "[oracle] Starting dateparser Oracle solution"

# Verify we have the source archive
SOURCE_ARCHIVE="/solution/source.tar.gz"
EXPECTED_SHA256="bab8c43a746266e68142f4926e69438ce551441aa88e54e78bb6410bf3ee7000"

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
if [ ! -f "pyproject.toml" ]; then
    echo "[oracle] ERROR: pyproject.toml not found after extraction" >&2
    exit 1
fi

if [ ! -d "dateparser" ]; then
    echo "[oracle] ERROR: dateparser directory not found after extraction" >&2
    exit 1
fi

echo "[oracle] Source extracted successfully"
echo "[oracle] Installing package"

# Install the package
pip install --no-cache-dir --no-build-isolation -e . || {
    echo "[oracle] ERROR: Installation failed" >&2
    exit 1
}

echo "[oracle] Verifying installation"
python3 -c "import dateparser; print(f'dateparser version: {dateparser.__version__}')" || {
    echo "[oracle] ERROR: Cannot import dateparser" >&2
    exit 1
}

echo "[oracle] Installation complete"
echo "[oracle] Oracle solution ready"
