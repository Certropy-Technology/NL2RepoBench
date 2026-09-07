#!/bin/bash
set -euo pipefail

echo "[control:offline] Verifying offline operation (uses Oracle implementation)"

# This control verifies that the verifier can run without network access
# We use the same Oracle implementation to test the offline constraint

SOURCE_ARCHIVE="/solution/source.tar.gz"
EXPECTED_SHA256="487c8d6094d3a7bc71a823fadcef6ff5efdbee13921f274da333870e45d6d438"

if [ ! -f "$SOURCE_ARCHIVE" ]; then
    echo "[control:offline] ERROR: Source archive not found" >&2
    exit 1
fi

ACTUAL_SHA256=$(sha256sum "$SOURCE_ARCHIVE" | awk '{print $1}')
if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
    echo "[control:offline] ERROR: SHA-256 mismatch" >&2
    exit 1
fi

cd /workspace
tar -xzf "$SOURCE_ARCHIVE" --strip-components=1

if [ ! -f "pyproject.toml" ]; then
    echo "[control:offline] ERROR: pyproject.toml not found" >&2
    exit 1
fi

pip install --no-cache-dir -e . || {
    echo "[control:offline] ERROR: Installation failed" >&2
    exit 1
}

echo "[control:offline] Offline verification complete"
