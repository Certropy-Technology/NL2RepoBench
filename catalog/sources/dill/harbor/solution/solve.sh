#!/usr/bin/env bash
set -euo pipefail

BUNDLE_DIR=$(dirname "$0")
EXPECTED_SHA256="423092df4182177d4d8ba8290c8a5b640c66ab35ec7da59ccfa00f6fa3eea5fa"
EXPECTED_REVISION="a9d4d39c411296fb3608c4ffd142134559942d21"

echo "=== Oracle solve.sh for dill ==="
echo "Bundle directory: $BUNDLE_DIR"

# Verify the source archive exists
if [ ! -f "$BUNDLE_DIR/dill-0.4.1.tar.gz" ]; then
    echo "ERROR: Source archive not found at $BUNDLE_DIR/dill-0.4.1.tar.gz"
    exit 1
fi

# Verify SHA256
echo "Verifying source archive integrity..."
ACTUAL_SHA256=$(sha256sum "$BUNDLE_DIR/dill-0.4.1.tar.gz" | cut -d' ' -f1)
if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
    echo "ERROR: SHA256 mismatch!"
    echo "  Expected: $EXPECTED_SHA256"
    echo "  Actual:   $ACTUAL_SHA256"
    exit 1
fi
echo "✓ SHA256 verified"

# Extract to /workspace
echo "Extracting source to /workspace..."
tar -xzf "$BUNDLE_DIR/dill-0.4.1.tar.gz" -C /workspace --strip-components=1

# Verify extraction
if [ ! -f /workspace/setup.py ]; then
    echo "ERROR: Extraction failed - setup.py not found in /workspace"
    exit 1
fi
echo "✓ Source extracted successfully"

# Install the package
echo "Installing dill..."
cd /workspace
python -m pip install --no-build-isolation --no-deps --no-index -e .

# Verify installation and imports
echo "Verifying installation..."
python -c "import dill; print(f'dill version: {dill.__version__}')"
python -c "import dill; assert dill.__version__ == '0.4.1', 'Version mismatch'"

# Verify key APIs
python -c "
import dill
# Test basic serialization
f = lambda x: x * 2
s = dill.dumps(f)
r = dill.loads(s)
assert r(5) == 10, 'Basic serialization failed'
print('✓ Basic serialization works')

# Test dump/load
import io
buffer = io.BytesIO()
dill.dump({'key': 'value'}, buffer)
buffer.seek(0)
data = dill.load(buffer)
assert data == {'key': 'value'}, 'dump/load failed'
print('✓ dump/load works')
"

echo "=== Oracle installation complete ==="
