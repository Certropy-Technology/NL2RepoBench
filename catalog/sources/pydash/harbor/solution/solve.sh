#!/bin/bash
set -euo pipefail

BUNDLE_DIR=$(dirname "$0")
EXPECTED_SHA256="30914c3e9d377ea2cd0d3c0a4f252889b08392f730a5eb4d117e5b598cdf1d52"
ARCHIVE_NAME="pydash-8.1.0.tar.gz"

# Verify source archive
ACTUAL_SHA256=$(sha256sum "$BUNDLE_DIR/$ARCHIVE_NAME" | cut -d' ' -f1)
if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
    echo "ERROR: SHA-256 mismatch for $ARCHIVE_NAME" >&2
    echo "Expected: $EXPECTED_SHA256" >&2
    echo "Actual:   $ACTUAL_SHA256" >&2
    exit 1
fi

# Extract to /workspace
cd /workspace
tar -xzf "$BUNDLE_DIR/$ARCHIVE_NAME" --strip-components=1

# Install the package
python -m pip install --no-build-isolation --no-deps --no-index -e .

# Verify imports
python -c "import pydash; print(f'pydash version: {pydash.__version__}')"
