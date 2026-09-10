#!/bin/bash
set -euo pipefail

BUNDLE_DIR=$(dirname "$0")
STAGING_ARCHIVE="$BUNDLE_DIR/astor-0.8.1.tar.gz"
EXPECTED_SHA256="6a6effda93f4e1ce9f618779b2dd1d9d84f1e32812c23a29b3fff6fd7f63fa5e"

echo "=== Oracle solve.sh for astor 0.8.1 ==="

# Verify source archive exists and matches expected SHA256
if [ ! -f "$STAGING_ARCHIVE" ]; then
    echo "ERROR: Source archive not found at $STAGING_ARCHIVE"
    exit 1
fi

ACTUAL_SHA256=$(sha256sum "$STAGING_ARCHIVE" | awk '{print $1}')
if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
    echo "ERROR: SHA256 mismatch"
    echo "  Expected: $EXPECTED_SHA256"
    echo "  Actual:   $ACTUAL_SHA256"
    exit 1
fi

echo "✓ Source archive verified: $EXPECTED_SHA256"

# Verify tar topology (should have astor-0.8.1/ prefix)
echo "Checking tar topology..."
TOP_LEVEL=$(tar -tzf "$STAGING_ARCHIVE" | head -1)
if [[ ! "$TOP_LEVEL" =~ ^astor-0\.8\.1/ ]]; then
    echo "ERROR: Unexpected tar topology, expected astor-0.8.1/ prefix"
    exit 1
fi

echo "✓ Tar topology verified"

# Extract to /workspace
cd /workspace
echo "Extracting to /workspace..."
tar -xzf "$STAGING_ARCHIVE"

# Move contents from astor-0.8.1/ to /workspace
if [ -d "astor-0.8.1" ]; then
    mv astor-0.8.1/* astor-0.8.1/.[!.]* . 2>/dev/null || mv astor-0.8.1/* .
    rmdir astor-0.8.1
fi

echo "✓ Extracted to /workspace"

# Install package
echo "Installing astor package..."
python -m pip install --no-build-isolation --no-deps --no-index -e . > /dev/null 2>&1

# Verify imports
echo "Verifying imports..."
python3 -c "import astor; import ast" || {
    echo "ERROR: Failed to import astor or ast"
    exit 1
}

echo "✓ Imports verified"

# Verify version
echo "Verifying version..."
INSTALLED_VERSION=$(python3 -c "import astor; print(astor.__version__)")
if [ "$INSTALLED_VERSION" != "0.8.1" ]; then
    echo "ERROR: Version mismatch, expected 0.8.1, got $INSTALLED_VERSION"
    exit 1
fi

echo "✓ Version verified: $INSTALLED_VERSION"

# Test basic functionality
echo "Testing basic functionality..."
python3 -c "
import ast
import astor
tree = ast.parse('x = 1')
result = astor.to_source(tree)
assert result == 'x = 1\n', f'Expected x = 1\\n, got {repr(result)}'
print('Basic functionality test passed')
"

echo "=== Oracle installation complete ==="
