#!/bin/bash
set -euo pipefail

# Oracle solution for jsonpatch task
# Restores the frozen reference implementation from bundled source

EXPECTED_REVISION="1ddce552cd1bdac5db3df931ba3df3bf9dac284c"
EXPECTED_DIGEST="27229586afe96571e8884a1f16170059cb08a43e05a9ff25241c1f8499ef9db6"

echo "=== Oracle Solution for jsonpatch ==="
echo "Expected revision: ${EXPECTED_REVISION}"
echo "Expected digest: ${EXPECTED_DIGEST}"

# Check if source archive is present
if [ ! -f /solution/source.tar.gz ]; then
    echo "ERROR: Source archive not found at /solution/source.tar.gz"
    exit 1
fi

# Verify source digest
ACTUAL_DIGEST=$(sha256sum /solution/source.tar.gz | cut -d' ' -f1)
echo "Source archive digest: ${ACTUAL_DIGEST}"

if [ "${ACTUAL_DIGEST}" != "${EXPECTED_DIGEST}" ]; then
    echo "ERROR: Source digest mismatch!"
    echo "  Expected: ${EXPECTED_DIGEST}"
    echo "  Actual:   ${ACTUAL_DIGEST}"
    exit 1
fi

echo "✓ Source digest verified"

# Extract to temporary location
TEMP_DIR=$(mktemp -d)
trap "rm -rf ${TEMP_DIR}" EXIT

echo "Extracting source archive..."
tar -xzf /solution/source.tar.gz -C "${TEMP_DIR}"

# Find the extracted directory (should be python-json-patch-<commit>)
EXTRACTED_DIR=$(find "${TEMP_DIR}" -maxdepth 1 -type d -name "python-json-patch-*" | head -1)

if [ -z "${EXTRACTED_DIR}" ]; then
    echo "ERROR: Could not find extracted source directory"
    ls -la "${TEMP_DIR}"
    exit 1
fi

echo "Found source directory: ${EXTRACTED_DIR}"

# Copy contents to /workspace, preserving structure
echo "Copying to /workspace..."
cp -r "${EXTRACTED_DIR}"/* /workspace/

# Verify key files exist
echo "Verifying package structure..."
if [ ! -f /workspace/jsonpatch.py ]; then
    echo "ERROR: jsonpatch.py not found in workspace"
    exit 1
fi

if [ ! -f /workspace/setup.py ]; then
    echo "ERROR: setup.py not found in workspace"
    exit 1
fi

if [ ! -d /workspace/bin ]; then
    echo "ERROR: bin/ directory not found in workspace"
    exit 1
fi

echo "✓ Package structure verified"

# List workspace contents
echo ""
echo "Workspace contents:"
ls -la /workspace/

echo ""
echo "=== Oracle solution completed successfully ==="
