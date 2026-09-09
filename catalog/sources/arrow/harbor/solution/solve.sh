#!/bin/bash
set -euo pipefail

BUNDLE_DIR=$(dirname "$0")
SOURCE_ARCHIVE="$BUNDLE_DIR/arrow-1.4.0.tar.gz"
EXPECTED_SHA256="ed0cc050e98001b8779e84d461b0098c4ac597e88704a655582b21d116e526d7"

# Verify source archive
echo "Verifying source archive..."
echo "$EXPECTED_SHA256  $SOURCE_ARCHIVE" | sha256sum -c -

# Extract to /workspace
echo "Extracting source to /workspace..."
cd /workspace
tar -xzf "$SOURCE_ARCHIVE" --strip-components=1

# Install the package
echo "Installing arrow..."
python -m pip install --no-build-isolation --no-deps --no-index -e .

# Verify installation
echo "Verifying installation..."
python -c "import arrow; print(f'arrow version: {arrow.__version__}')"

echo "Oracle setup complete."
