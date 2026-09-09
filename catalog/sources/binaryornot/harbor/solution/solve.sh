#!/bin/bash
set -euo pipefail

BUNDLE_DIR=$(dirname "$0")
EXPECTED_SHA256="cc8d57cfa71d74ff8c28a7726734d53a851d02fad9e3a5581fb807f989f702f0"
ARCHIVE="binaryornot-0.6.0.tar.gz"

cd "$BUNDLE_DIR"

# Verify archive
echo "Verifying source archive..."
ACTUAL_SHA256=$(sha256sum "$ARCHIVE" | awk '{print $1}')
if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
    echo "ERROR: SHA-256 mismatch!"
    echo "Expected: $EXPECTED_SHA256"
    echo "Actual:   $ACTUAL_SHA256"
    exit 1
fi

# Extract to /workspace
echo "Extracting to /workspace..."
tar -xzf "$ARCHIVE" -C /workspace --strip-components=1

# Install
echo "Installing binaryornot..."
cd /workspace
python -m pip install --no-build-isolation --no-deps --no-index -e .

# Verify imports
echo "Verifying installation..."
python -c "from binaryornot.check import is_binary; from binaryornot.helpers import is_binary_string, has_binary_extension, get_starting_chunk; print('✓ All imports successful')"

echo "Oracle setup complete!"
