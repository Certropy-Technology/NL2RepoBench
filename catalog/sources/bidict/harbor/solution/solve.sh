#!/bin/bash
set -euo pipefail

BUNDLE_DIR="$(dirname "$0")"
WORKSPACE="${WORKSPACE:-/workspace}"

# Source metadata
SOURCE_DIGEST="sha256:27053e00a1fea61de40cafa4e0f455dfa0d13fee8f898e25d7684954d05d0ca8"
SOURCE_ARCHIVE="${BUNDLE_DIR}/bidict-source.tar.gz"
EXPECTED_COMMIT="2798f6088c0b233ddfc5f1d20cb253623a41223d"

echo "[solve.sh] Extracting source archive..."
if [ ! -f "$SOURCE_ARCHIVE" ]; then
    echo "ERROR: Source archive not found: $SOURCE_ARCHIVE" >&2
    exit 1
fi

# Verify digest
ACTUAL_DIGEST="sha256:$(sha256sum "$SOURCE_ARCHIVE" | cut -d' ' -f1)"
if [ "$ACTUAL_DIGEST" != "$SOURCE_DIGEST" ]; then
    echo "ERROR: Source digest mismatch" >&2
    echo "  Expected: $SOURCE_DIGEST" >&2
    echo "  Actual:   $ACTUAL_DIGEST" >&2
    exit 1
fi

# Extract to workspace
cd "$WORKSPACE"
tar -xzf "$SOURCE_ARCHIVE" --strip-components=1

echo "[solve.sh] Installing bidict..."
python3 -m pip install --no-build-isolation --no-deps --no-index -e . >/dev/null 2>&1

echo "[solve.sh] Verifying installation..."
python3 -c "from bidict import bidict; print('bidict imported successfully')"

echo "[solve.sh] Oracle solution ready"
