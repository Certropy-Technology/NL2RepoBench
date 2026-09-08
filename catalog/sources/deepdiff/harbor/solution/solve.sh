#!/bin/bash
set -euo pipefail

BUNDLE_DIR=$(dirname "$0")
EXPECTED_SHA256="07e9e366fab4297755153c4eab795ad4ef3cbd0d51660e847f5751c6bd727687"
EXPECTED_COMMIT="c59636cda63cd3951777208c783285e6bf634159"
SOURCE_TAR="${BUNDLE_DIR}/deepdiff-9.1.0.tar.gz"

echo "=== DeepDiff Oracle Solution ==="
echo "Verifying source archive..."

# Verify SHA256
ACTUAL_SHA256=$(sha256sum "${SOURCE_TAR}" | cut -d' ' -f1)
if [ "${ACTUAL_SHA256}" != "${EXPECTED_SHA256}" ]; then
    echo "ERROR: SHA256 mismatch!"
    echo "Expected: ${EXPECTED_SHA256}"
    echo "Actual: ${ACTUAL_SHA256}"
    exit 1
fi
echo "✓ SHA256 verified: ${EXPECTED_SHA256}"

# Extract to /workspace
echo "Extracting source to /workspace..."
cd /workspace
tar -xzf "${SOURCE_TAR}"

# Verify extraction
if [ ! -d "deepdiff-9.1.0" ]; then
    echo "ERROR: Expected directory deepdiff-9.1.0 not found!"
    exit 1
fi

cd deepdiff-9.1.0

# Verify the version in pyproject.toml
echo "Verifying version..."
if ! grep -q 'version = "9.1.0"' pyproject.toml 2>/dev/null; then
    echo "WARNING: Could not verify version in pyproject.toml"
fi

# Install the package
echo "Installing deepdiff..."
python3 -m pip install --no-build-isolation --no-deps --no-index -e . > /dev/null 2>&1

# Verify installation and imports
echo "Verifying installation..."
python3 -c "from deepdiff import DeepDiff; print(f'✓ DeepDiff imported successfully')"
python3 -c "from deepdiff import DeepSearch, DeepHash, Delta; print(f'✓ Additional exports verified')"

# Verify basic functionality
python3 << 'VERIFY_EOF'
from deepdiff import DeepDiff
result = DeepDiff({'a': 1}, {'a': 2})
assert 'values_changed' in result.to_dict()
print("✓ Basic functionality verified")
VERIFY_EOF

echo "=== Oracle solution complete ==="
