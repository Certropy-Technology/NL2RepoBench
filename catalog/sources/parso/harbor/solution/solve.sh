#!/usr/bin/env bash
set -euo pipefail

BUNDLE_DIR=$(dirname "$0")
EXPECTED_SHA256="eaaac4c9fdd5e9e8852dc778d2d7405897ec510f2a298071453e5e3a07914bb1"
EXPECTED_VERSION="0.8.7"

# Verify the source archive exists
if [ ! -f "$BUNDLE_DIR/parso-$EXPECTED_VERSION.tar.gz" ]; then
    echo "ERROR: Source archive parso-$EXPECTED_VERSION.tar.gz not found in $BUNDLE_DIR" >&2
    exit 1
fi

# Verify SHA256
echo "Verifying source archive integrity..."
ACTUAL_SHA256=$(sha256sum "$BUNDLE_DIR/parso-$EXPECTED_VERSION.tar.gz" | cut -d' ' -f1)
if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
    echo "ERROR: SHA256 mismatch. Expected $EXPECTED_SHA256, got $ACTUAL_SHA256" >&2
    exit 1
fi
echo "✓ SHA256 verified: $EXPECTED_SHA256"

# Extract to /workspace
echo "Extracting source to /workspace..."
cd /workspace
tar -xzf "$BUNDLE_DIR/parso-$EXPECTED_VERSION.tar.gz" --strip-components=1

# Verify the extraction
if [ ! -f "setup.py" ]; then
    echo "ERROR: setup.py not found after extraction" >&2
    exit 1
fi

# Install the package
echo "Installing parso..."
python -m pip install --no-build-isolation --no-deps --no-index -e .

# Verify the installation
echo "Verifying installation..."
python -c "import parso; print(f'parso version: {parso.__version__}')"

INSTALLED_VERSION=$(python -c "import parso; print(parso.__version__)")
if [ "$INSTALLED_VERSION" != "$EXPECTED_VERSION" ]; then
    echo "ERROR: Version mismatch. Expected $EXPECTED_VERSION, got $INSTALLED_VERSION" >&2
    exit 1
fi

echo "✓ parso $EXPECTED_VERSION successfully installed"
