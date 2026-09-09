#!/usr/bin/env bash
set -euo pipefail

BUNDLE_DIR="$(cd "$(dirname "$0")" && pwd)"
EXPECTED_SHA256="5a1c6005c858c13c2575a31bd1cc7a5a63184e63e55db5affb2e991232b23e9c"

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

# Extract to /workspace (no strip-components since we packed without top-level dir)
cd /workspace
tar -xzf "$BUNDLE_DIR/source.tar.gz"

# Verify extraction
if [ ! -f "/workspace/pyproject.toml" ]; then
    echo "ERROR: pyproject.toml not found after extraction" >&2
    exit 1
fi

# Install the package
python -m pip install --no-build-isolation --no-deps --no-index .

# Verify installation
python -c "import tabulate; print(f'tabulate {tabulate.__version__} installed')"

exit 0
