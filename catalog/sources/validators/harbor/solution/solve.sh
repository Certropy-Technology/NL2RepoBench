#!/usr/bin/env bash
set -euo pipefail

BUNDLE_DIR="$(cd "$(dirname "$0")" && pwd)"
EXPECTED_SHA256="992d6c48a4e77c81f1b4daba10d16c3a9bb0dbb79b3a19ea847ff0928e70497a"

cd "$BUNDLE_DIR"

# Verify source archive
echo "Verifying source archive..."
echo "$EXPECTED_SHA256  source.tar.gz" | sha256sum -c -

# Extract to /workspace
echo "Extracting source to /workspace..."
mkdir -p /workspace
cd /workspace
tar -xzf "$BUNDLE_DIR/source.tar.gz" --strip-components=1

# Install the package
echo "Installing validators package..."
python -m pip install --no-build-isolation --no-deps --no-index -e .

# Verify import
echo "Verifying installation..."
python -c "import validators; print(f'validators {validators.__version__} installed successfully')"

echo "Oracle solution installed successfully."
