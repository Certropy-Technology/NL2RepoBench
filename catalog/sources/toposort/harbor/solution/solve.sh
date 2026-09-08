#!/bin/bash
set -euo pipefail

BUNDLE_DIR=$(dirname "$0")

# Expected source digest
EXPECTED_SHA256="bfbb479c53d0a696ea7402601f4e693c97b0367837c8898bc6471adfca37a6bd"
EXPECTED_COMMIT="e67c242ceec5908564837ce6ac2cb661659b0cc8"

# Archive path
ARCHIVE="$BUNDLE_DIR/toposort-1.10.tar.gz"

# Verify the archive exists and matches expected digest
if [ ! -f "$ARCHIVE" ]; then
    echo "ERROR: Archive not found at $ARCHIVE" >&2
    exit 1
fi

ACTUAL_SHA256=$(sha256sum "$ARCHIVE" | cut -d' ' -f1)
if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
    echo "ERROR: SHA256 mismatch for archive" >&2
    echo "Expected: $EXPECTED_SHA256" >&2
    echo "Actual: $ACTUAL_SHA256" >&2
    exit 1
fi

echo "Archive verified: $ARCHIVE"

# Extract to /workspace
cd /workspace
tar -xzf "$ARCHIVE" --strip-components=1
echo "Extracted to /workspace"

# Verify we have the source file
if [ ! -f "/workspace/src/toposort.py" ]; then
    echo "ERROR: toposort.py not found after extraction" >&2
    exit 1
fi

# Install the package
cd /workspace
python -m pip install --no-build-isolation --no-deps --no-index -e .

# Verify import
python -c "import toposort; print(f'toposort version: {toposort.__version__}')"
python -c "from toposort import toposort, toposort_flatten, CircularDependencyError; print('All imports successful')"

echo "Oracle solution installed successfully"
