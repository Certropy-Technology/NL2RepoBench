#!/bin/bash
set -euo pipefail

BUNDLE_DIR=$(dirname "$0")
EXPECTED_SHA256="69192b8e5c0a7d0dc5ff1187eeb3e398141633a4bde51c69c87f58fe87ed361c"
ARCHIVE_NAME="wcag-contrast-ratio-0.9.tar.gz"

# Verify source archive integrity before use
ACTUAL_SHA256=$(sha256sum "$BUNDLE_DIR/$ARCHIVE_NAME" | cut -d' ' -f1)
if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
    echo "ERROR: SHA-256 mismatch for $ARCHIVE_NAME" >&2
    echo "Expected: $EXPECTED_SHA256" >&2
    echo "Actual:   $ACTUAL_SHA256" >&2
    exit 1
fi

# Extract the frozen upstream tree into the workspace
cd /workspace
tar -xzf "$BUNDLE_DIR/$ARCHIVE_NAME" --strip-components=1

# Install the package from the extracted source
python -m pip install --no-build-isolation --no-deps --no-index -e .

# Verify the public import surface resolves
python -c "import wcag_contrast_ratio; print('wcag_contrast_ratio installed')"
