#!/bin/bash
set -euo pipefail

echo "[oracle] Starting phonenumbers Oracle solution"

# Verify we have the source archive
SOURCE_ARCHIVE="/solution/source.tar.gz"
EXPECTED_SHA256="6806bebd46638af2fc2609675ea046067a40512eca81bf1446132e2fda29d113"

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

if [ ! -d "phonenumbers" ]; then
    echo "[oracle] ERROR: phonenumbers directory not found after extraction" >&2
    exit 1
fi

echo "[oracle] Source extracted successfully"

# Check if we need to patch version (setuptools dynamic version)
if ! grep -q '^__version__' phonenumbers/__init__.py 2>/dev/null; then
    echo "[oracle] WARNING: __version__ not found in phonenumbers/__init__.py" >&2
fi

echo "[oracle] Installing package"

# Install the package
pip install --no-cache-dir --no-build-isolation -e . || {
    echo "[oracle] ERROR: Installation failed" >&2
    exit 1
}

echo "[oracle] Verifying installation"

# Verify imports
python3 -c "import phonenumbers; print(f'phonenumbers version: {phonenumbers.__version__}')" || {
    echo "[oracle] ERROR: Import verification failed" >&2
    exit 1
}

# Verify core functionality
python3 -c "import phonenumbers; num = phonenumbers.parse('+14155552671', None); assert num.country_code == 1" || {
    echo "[oracle] ERROR: Basic functionality test failed" >&2
    exit 1
}

echo "[oracle] Installation complete"
echo "[oracle] Oracle solution ready"
