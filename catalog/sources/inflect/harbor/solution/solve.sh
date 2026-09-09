#!/bin/bash
set -euo pipefail

BUNDLE_DIR=$(dirname "$0")
EXPECTED_SHA256="faf19801c3742ed5a05a8ce388e0d8fe1a07f8d095c82201eb904f5d27ad571f"
ARCHIVE="inflect-7.5.0.tar.gz"

# Verify the archive exists
if [ ! -f "$BUNDLE_DIR/$ARCHIVE" ]; then
    echo "Error: Archive $ARCHIVE not found in bundle" >&2
    exit 1
fi

# Verify SHA-256 checksum
echo "Verifying SHA-256 checksum..."
ACTUAL_SHA256=$(sha256sum "$BUNDLE_DIR/$ARCHIVE" | cut -d' ' -f1)
if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
    echo "Error: SHA-256 mismatch" >&2
    echo "Expected: $EXPECTED_SHA256" >&2
    echo "Actual:   $ACTUAL_SHA256" >&2
    exit 1
fi
echo "SHA-256 verified: $EXPECTED_SHA256"

# Extract to /workspace
echo "Extracting archive to /workspace..."
cd /workspace
tar -xzf "$BUNDLE_DIR/$ARCHIVE" --strip-components=1

# Install the package
echo "Installing inflect package..."
python -m pip install --no-build-isolation --no-deps --no-index -e .

# Verify imports
echo "Verifying inflect can be imported..."
python -c "import inflect; p = inflect.engine(); print('inflect version:', p)" || {
    echo "Error: Failed to import inflect" >&2
    exit 1
}

echo "Oracle setup complete."
