#!/bin/bash
set -euo pipefail

BUNDLE_DIR=$(dirname "$0")
EXPECTED_SHA256="d128512515fbf4612e0ff21fd6380399210318b7b54a9af59dff8454cf9730eb"

# Verify source archive
ACTUAL_SHA256=$(sha256sum "$BUNDLE_DIR/wcwidth-0.8.3.tar.gz" | cut -d' ' -f1)
if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
    echo "ERROR: SHA256 mismatch for wcwidth-0.8.3.tar.gz"
    echo "Expected: $EXPECTED_SHA256"
    echo "Got: $ACTUAL_SHA256"
    exit 1
fi

# Extract to /workspace
cd /workspace
tar -xzf "$BUNDLE_DIR/wcwidth-0.8.3.tar.gz"

# Check topology
if [ ! -d "/workspace/wcwidth-0.8.3" ]; then
    echo "ERROR: Expected wcwidth-0.8.3 directory not found"
    exit 1
fi

# Install
pip install --no-index --no-deps /workspace/wcwidth-0.8.3

# Verify imports
python3 -c "import wcwidth; assert wcwidth.__version__ == '0.8.3', f'Version mismatch: {wcwidth.__version__}'"

echo "Oracle solution installed successfully"
