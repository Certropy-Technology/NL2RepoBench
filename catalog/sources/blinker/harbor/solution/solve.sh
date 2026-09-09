#!/usr/bin/env bash
set -euo pipefail

BUNDLE_DIR=$(dirname "$0")

# Expected source digest and revision
EXPECTED_REVISION="669f3a027828d19786e708b511277fabcd6b9532"
EXPECTED_DIGEST="b4ce2265a7abece45e7cc896e98dbebe6cead56bcf805a3d23136d145f5445bf"

# Source archive should be in the bundle
ARCHIVE="$BUNDLE_DIR/blinker-1.9.0.tar.gz"

if [ ! -f "$ARCHIVE" ]; then
    echo "ERROR: Source archive not found: $ARCHIVE" >&2
    exit 1
fi

# Verify sha256
ACTUAL_DIGEST=$(sha256sum "$ARCHIVE" | cut -d' ' -f1)
if [ "$ACTUAL_DIGEST" != "$EXPECTED_DIGEST" ]; then
    echo "ERROR: Source digest mismatch" >&2
    echo "  Expected: $EXPECTED_DIGEST" >&2
    echo "  Actual:   $ACTUAL_DIGEST" >&2
    exit 1
fi

# Extract to /workspace
cd /workspace
tar -xzf "$ARCHIVE" --strip-components=1

# Install the package
python -m pip install --no-build-isolation --no-deps --no-index -e .

# Verify import
python -c "import blinker; print(f'blinker imported successfully')"

echo "Oracle solution installed successfully"
