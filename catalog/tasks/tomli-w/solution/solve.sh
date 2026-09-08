#!/bin/bash
set -euo pipefail

# Oracle solution for tomli-w
# Extracts the frozen reference source and installs it into /workspace

EXPECTED_REVISION="87e98b1cb9ee0ba1ac28fa7c430dc9af5045ced5"
EXPECTED_SHA256="5b2f86791b0b23b75320ed90096589fbf507895bba7d4f220afd76d4fc5798ee"

echo "=== Oracle Solution: tomli-w ==="

# Verify we have the source archive
if [ ! -f "/solution/source.tar.gz" ]; then
    echo "ERROR: Source archive not found at /solution/source.tar.gz"
    exit 1
fi

# Verify SHA-256
echo "Verifying source archive integrity..."
ACTUAL_SHA256=$(sha256sum /solution/source.tar.gz | awk '{print $1}')
if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
    echo "ERROR: SHA-256 mismatch"
    echo "Expected: $EXPECTED_SHA256"
    echo "Got:      $ACTUAL_SHA256"
    exit 1
fi
echo "SHA-256 verified: $EXPECTED_SHA256"

# Extract to temporary directory
TEMP_DIR=$(mktemp -d)
echo "Extracting source to $TEMP_DIR..."
tar -xzf /solution/source.tar.gz -C "$TEMP_DIR"

# Find the extracted directory (should be tomli-w-<commit>)
SOURCE_DIR=$(find "$TEMP_DIR" -maxdepth 1 -type d -name "tomli-w-*" | head -1)
if [ -z "$SOURCE_DIR" ]; then
    echo "ERROR: Could not find extracted source directory"
    ls -la "$TEMP_DIR"
    exit 1
fi

echo "Found source directory: $SOURCE_DIR"

# Verify it's the correct revision by checking pyproject.toml version
if [ -f "$SOURCE_DIR/pyproject.toml" ]; then
    if grep -q 'version = "1.2.0"' "$SOURCE_DIR/pyproject.toml"; then
        echo "Version check passed: 1.2.0"
    else
        echo "WARNING: Version mismatch in pyproject.toml"
    fi
else
    echo "WARNING: pyproject.toml not found"
fi

# Copy to /workspace
echo "Installing source to /workspace..."
cp -r "$SOURCE_DIR"/. /workspace/

# Verify structure
echo "Verifying workspace structure..."
if [ ! -f "/workspace/pyproject.toml" ]; then
    echo "ERROR: pyproject.toml not found in /workspace"
    exit 1
fi

if [ ! -d "/workspace/src/tomli_w" ]; then
    echo "ERROR: src/tomli_w not found in /workspace"
    exit 1
fi

echo "Workspace structure verified"

# Clean up
rm -rf "$TEMP_DIR"

echo "=== Oracle solution complete ==="
