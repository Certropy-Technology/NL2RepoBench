#!/usr/bin/env bash
set -euo pipefail

# Offline control - verifies verifier works without network
# This is the Oracle but in a no-network environment

echo "=== Offline control ==="

EXPECTED_REVISION="0980eb52aa867fc32f70859a61c0609501b73a99"
EXPECTED_SHA256="c43f9ad2ed38f168bb84666a70ac8c645b648eac1cab10b79438971af48f2290"

# The source archive should be bundled
SOURCE_ARCHIVE="/oracle/source-${EXPECTED_REVISION}.tar.gz"

if [ ! -f "$SOURCE_ARCHIVE" ]; then
    echo "ERROR: Source archive not found at $SOURCE_ARCHIVE"
    exit 1
fi

# Verify SHA-256
ACTUAL_SHA256=$(sha256sum "$SOURCE_ARCHIVE" | cut -d' ' -f1)
if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
    echo "ERROR: Source archive SHA-256 mismatch"
    exit 1
fi

# Extract to temporary directory
TEMP_DIR=$(mktemp -d)
trap "rm -rf '$TEMP_DIR'" EXIT

cd "$TEMP_DIR"
tar -xzf "$SOURCE_ARCHIVE"

SOURCE_DIR=$(find . -maxdepth 1 -type d -name "termcolor-*" | head -1)
cd "$SOURCE_DIR"
cp -r * /workspace/
cp -r .* /workspace/ 2>/dev/null || true

cd /workspace

# Install offline
export SETUPTOOLS_SCM_PRETEND_VERSION=3.3.0
pip install --no-cache-dir . || exit 1

echo "=== Offline control complete ==="
