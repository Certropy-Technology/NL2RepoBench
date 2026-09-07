#!/usr/bin/env bash
set -euo pipefail

EXPECTED_SOURCE_SHA256="82da501eb24ba60494eb86f1ba6c517d566758031832153bbbcc55424b0273fe"
SOURCE_FILE="/solution/source.tar.gz"

echo "[solve.sh] Verifying frozen source archive..."
if [ ! -f "$SOURCE_FILE" ]; then
    echo "ERROR: Source archive $SOURCE_FILE not found in oracle bundle" >&2
    exit 1
fi

ACTUAL_SHA256=$(sha256sum "$SOURCE_FILE" | cut -d' ' -f1)
if [ "$ACTUAL_SHA256" != "$EXPECTED_SOURCE_SHA256" ]; then
    echo "ERROR: Source SHA-256 mismatch" >&2
    echo "  Expected: $EXPECTED_SOURCE_SHA256" >&2
    echo "  Actual:   $ACTUAL_SHA256" >&2
    exit 1
fi

echo "[solve.sh] Extracting source to /workspace..."
cd /workspace
tar -xzf "$SOURCE_FILE"

echo "[solve.sh] Installing pyperf with --no-build-isolation..."
pip install --no-build-isolation --no-deps --no-index -e /workspace

echo "[solve.sh] Verifying installation..."
python3 -c "import pyperf; print(f'pyperf installed')"

echo "[solve.sh] Oracle solution installed successfully"
