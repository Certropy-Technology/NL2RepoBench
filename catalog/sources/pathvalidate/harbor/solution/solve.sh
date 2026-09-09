#!/bin/bash
set -euo pipefail

BUNDLE_DIR="$(dirname "$0")"
EXPECTED_SHA256="b18c07212bfead624345bb8e1d6141cdcf15a39736994ea0b94035ad2b1ba177"
ARCHIVE_NAME="pathvalidate-3.3.1.tar.gz"

echo "[solve.sh] Verifying source archive..."
cd "$BUNDLE_DIR"

if [ ! -f "$ARCHIVE_NAME" ]; then
    echo "Error: $ARCHIVE_NAME not found in bundle"
    exit 1
fi

# Verify SHA-256
ACTUAL_SHA256=$(sha256sum "$ARCHIVE_NAME" | cut -d' ' -f1)
if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
    echo "Error: SHA-256 mismatch"
    echo "  Expected: $EXPECTED_SHA256"
    echo "  Actual:   $ACTUAL_SHA256"
    exit 1
fi
echo "[solve.sh] SHA-256 verified: $EXPECTED_SHA256"

# Extract to /workspace
echo "[solve.sh] Extracting source to /workspace..."
tar -xzf "$ARCHIVE_NAME" -C /workspace --strip-components=1

# Verify extraction
if [ ! -f /workspace/setup.py ]; then
    echo "Error: Extraction failed - setup.py not found"
    exit 1
fi

cd /workspace

# Install the package
echo "[solve.sh] Installing pathvalidate..."
python -m pip install --no-build-isolation --no-deps --no-index -e . > /tmp/install.log 2>&1

# Verify installation
echo "[solve.sh] Verifying installation..."
python << 'EOFPY'
import sys
try:
    import pathvalidate
    print(f"[solve.sh] Successfully imported pathvalidate")
    print(f"[solve.sh] Version: {pathvalidate.__version__}")
    
    # Verify core API
    from pathvalidate import (
        validate_filename, sanitize_filename, is_valid_filename,
        validate_filepath, sanitize_filepath, is_valid_filepath,
        Platform, ErrorReason, ValidationError
    )
    print("[solve.sh] Core API verified")
    
    # Quick smoke test
    assert is_valid_filename('test.txt') == True
    assert is_valid_filename('COM1') == False
    assert sanitize_filename('file:name.txt') == 'filename.txt'
    print("[solve.sh] Smoke tests passed")
    
except Exception as e:
    print(f"[solve.sh] Import/verification failed: {e}", file=sys.stderr)
    sys.exit(1)
EOFPY

echo "[solve.sh] Installation complete and verified"
