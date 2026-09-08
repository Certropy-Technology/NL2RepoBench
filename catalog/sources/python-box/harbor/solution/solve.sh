#!/bin/bash
set -euo pipefail

# Oracle solution script for python-box
# Extracts frozen source and installs into /workspace

BUNDLE_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE_ARCHIVE="$BUNDLE_DIR/source.tar.gz"
EXPECTED_SHA256="e412e36c25fca8223560516d53ef6c7993591c3b0ec8bb4ec582bf7defdd79f0"

# Verify source archive exists
if [[ ! -f "$SOURCE_ARCHIVE" ]]; then
    echo "ERROR: Source archive not found at $SOURCE_ARCHIVE" >&2
    exit 1
fi

# Verify SHA256
ACTUAL_SHA256=$(sha256sum "$SOURCE_ARCHIVE" | cut -d' ' -f1)
if [[ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]]; then
    echo "ERROR: Source archive SHA256 mismatch" >&2
    echo "Expected: $EXPECTED_SHA256" >&2
    echo "Got:      $ACTUAL_SHA256" >&2
    exit 1
fi

# Extract to /workspace
# The tarball has a top-level directory python_box-7.4.1/ so we use --strip-components=1
cd /workspace
tar -xzf "$SOURCE_ARCHIVE" --strip-components=1

# Verify key files exist
if [[ ! -f "setup.py" ]] || [[ ! -d "box" ]]; then
    echo "ERROR: Expected setup.py and box/ directory not found after extraction" >&2
    exit 1
fi

# Install the package in editable mode
python -m pip install --no-build-isolation --no-deps --no-index -e .

# Verify installation
python -c "from box import Box; print('python-box installed successfully, version:', Box.__module__)"

echo "Oracle solution complete"
