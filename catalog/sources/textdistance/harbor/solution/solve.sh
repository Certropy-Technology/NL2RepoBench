#!/bin/bash
set -euo pipefail

# TextDistance Oracle solution - fetch and install reference implementation

BUNDLE_DIR=$(dirname "$(readlink -f "$0")")
EXPECTED_SHA256="d6dabc50b4ea832cdcf0e1e6021bd0c7fcd9ade155888d79bb6a3c31fce2dc6f"
EXPECTED_COMMIT="faa25f6ff50d0f34dc9655d4d7b0d8daf6f9ff85"
ARCHIVE_NAME="textdistance-4.6.3.tar.gz"

echo "[Oracle] Verifying source archive..."
if [ ! -f "$BUNDLE_DIR/$ARCHIVE_NAME" ]; then
    echo "ERROR: Source archive not found: $BUNDLE_DIR/$ARCHIVE_NAME"
    exit 1
fi

# Verify SHA256
ACTUAL_SHA256=$(sha256sum "$BUNDLE_DIR/$ARCHIVE_NAME" | cut -d' ' -f1)
if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
    echo "ERROR: SHA256 mismatch!"
    echo "  Expected: $EXPECTED_SHA256"
    echo "  Actual:   $ACTUAL_SHA256"
    exit 1
fi
echo "[Oracle] SHA256 verified: $EXPECTED_SHA256"

# Extract to workspace
echo "[Oracle] Extracting to /workspace..."
cd /workspace
tar -xzf "$BUNDLE_DIR/$ARCHIVE_NAME" --strip-components=1

# Verify we have the expected structure
if [ ! -f "setup.py" ] || [ ! -d "textdistance" ]; then
    echo "ERROR: Unexpected archive structure"
    exit 1
fi

# Install the package
echo "[Oracle] Installing textdistance..."
python -m pip install --no-build-isolation --no-deps --no-index -e . > /dev/null 2>&1

# Verify installation
echo "[Oracle] Verifying installation..."
python -c "import textdistance; print(f'textdistance version: {textdistance.__version__}')"

# Test core imports
python -c "
import textdistance
# Test that core functions are available
assert hasattr(textdistance, 'hamming')
assert hasattr(textdistance, 'levenshtein')
assert hasattr(textdistance, 'jaro_winkler')
assert hasattr(textdistance, 'jaccard')
assert hasattr(textdistance, 'damerau_levenshtein')
assert hasattr(textdistance, 'lcsseq')
assert hasattr(textdistance, 'ratcliff_obershelp')
assert hasattr(textdistance, 'cosine')
print('[Oracle] All core functions verified')
"

echo "[Oracle] Solution installation complete"
