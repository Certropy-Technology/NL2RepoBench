#!/usr/bin/env bash
set -euo pipefail

BUNDLE_DIR="$(cd "$(dirname "$0")" && pwd)"
EXPECTED_SHA256="1a29730d366e996aaacffb2f1f1cb9593dc38e2ddd30c91250c6dde09ea9b417"

# Verify source archive exists
if [ ! -f "$BUNDLE_DIR/source.tar.gz" ]; then
    echo "ERROR: source.tar.gz not found in bundle" >&2
    exit 1
fi

# Verify SHA256
ACTUAL_SHA256=$(sha256sum "$BUNDLE_DIR/source.tar.gz" | cut -d' ' -f1)
if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
    echo "ERROR: source.tar.gz SHA256 mismatch" >&2
    echo "Expected: $EXPECTED_SHA256" >&2
    echo "Actual:   $ACTUAL_SHA256" >&2
    exit 1
fi

# Extract to /workspace with --strip-components=1 (tar has inflection-0.5.1/ prefix)
cd /workspace
tar -xzf "$BUNDLE_DIR/source.tar.gz" --strip-components=1

# Verify extraction
if [ ! -f "/workspace/setup.py" ]; then
    echo "ERROR: setup.py not found after extraction" >&2
    exit 1
fi

# Install package
python -m pip install --no-build-isolation --no-deps --no-index -e .

# Verify import
python -c "import inflection; assert inflection.__version__ == '0.5.1'"

echo "Oracle solution installed successfully"
