#!/bin/bash
set -euo pipefail

BUNDLE_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE_ARCHIVE="$BUNDLE_DIR/source.tar.gz"
EXPECTED_SHA256="48e8f4d9e7e5878571ecf6f2b4e57634f93cd474cc8cfbd2376f2d11b396e30d"

# Verify source archive exists
if [ ! -f "$SOURCE_ARCHIVE" ]; then
    echo "ERROR: Source archive not found at $SOURCE_ARCHIVE" >&2
    exit 1
fi

# Verify SHA-256
ACTUAL_SHA256=$(sha256sum "$SOURCE_ARCHIVE" | awk '{print $1}')
if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
    echo "ERROR: SHA-256 mismatch" >&2
    echo "Expected: $EXPECTED_SHA256" >&2
    echo "Got:      $ACTUAL_SHA256" >&2
    exit 1
fi

# Extract to /workspace
# The tarball has a top-level directory more_itertools-11.1.0/
cd /workspace
tar -xzf "$SOURCE_ARCHIVE" --strip-components=1

# Verify extraction
if [ ! -f "/workspace/pyproject.toml" ]; then
    echo "ERROR: pyproject.toml not found after extraction" >&2
    exit 1
fi

# Install the package
python -m pip install --no-build-isolation --no-deps --no-index -e .

# Verify installation
python -c "import more_itertools; print(f'more-itertools {more_itertools.__version__} installed')"

exit 0
