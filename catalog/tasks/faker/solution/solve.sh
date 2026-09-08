#!/bin/bash
set -euo pipefail

BUNDLE_DIR="$(cd "$(dirname "$0")" && pwd)"
EXPECTED_SHA="581d21fe695a061e9c3872454fb9c1cbf524afd260193da90385af2ce235d791"

# Verify source archive exists and matches expected digest
if [ ! -f "$BUNDLE_DIR/source.tar.gz" ]; then
    echo "ERROR: source.tar.gz not found in bundle" >&2
    exit 1
fi

ACTUAL_SHA=$(sha256sum "$BUNDLE_DIR/source.tar.gz" | cut -d' ' -f1)
if [ "$ACTUAL_SHA" != "$EXPECTED_SHA" ]; then
    echo "ERROR: SHA256 mismatch" >&2
    echo "  Expected: $EXPECTED_SHA" >&2
    echo "  Actual:   $ACTUAL_SHA" >&2
    exit 1
fi

# Extract to workspace
cd /workspace
tar -xzf "$BUNDLE_DIR/source.tar.gz" --strip-components=1

# Install package
python -m pip install --no-build-isolation --no-deps --no-index -e .

# Verify import
python -c "from faker import Faker; print('Faker imported successfully')"

exit 0
