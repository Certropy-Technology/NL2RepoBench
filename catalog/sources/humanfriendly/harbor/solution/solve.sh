#!/bin/bash
set -euo pipefail

BUNDLE_DIR=$(dirname "$0")
EXPECTED_SHA256="6b0b831ce8f15f7300721aa49829fc4e83921a9a301cc7f606be6686a2288ddc"
SOURCE_ARCHIVE="$BUNDLE_DIR/humanfriendly-10.0.tar.gz"

# Verify SHA256
ACTUAL_SHA256=$(sha256sum "$SOURCE_ARCHIVE" | cut -d' ' -f1)
if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
    echo "SHA256 mismatch: expected $EXPECTED_SHA256, got $ACTUAL_SHA256" >&2
    exit 1
fi

# Extract to /workspace
cd /workspace
tar -xzf "$SOURCE_ARCHIVE" --strip-components=1

# Install the package
python -m pip install --no-build-isolation --no-deps --no-index -e .

# Verify imports
python -c "import humanfriendly; print(f'humanfriendly version: {humanfriendly.__version__}')"
python -c "from humanfriendly import format_size, parse_size, format_timespan, parse_timespan; print('Core imports successful')"
python -c "from humanfriendly.text import pluralize, concatenate; print('Text module imports successful')"

echo "Oracle solution installed successfully"
