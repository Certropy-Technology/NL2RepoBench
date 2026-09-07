#!/usr/bin/env bash
set -euo pipefail

EXPECTED_WHEEL_SHA256="da1892f7dda4d1746531bc15c4b06ee43893cc9ea3b1a95f57e7a8fce612ff6d"
WHEEL_FILE="/solution/pyperf-2.10.0-py3-none-any.whl"

echo "[solve.sh] Verifying pre-built wheel..."
if [ ! -f "$WHEEL_FILE" ]; then
    echo "ERROR: Wheel file $WHEEL_FILE not found in oracle bundle" >&2
    exit 1
fi

ACTUAL_SHA256=$(sha256sum "$WHEEL_FILE" | cut -d' ' -f1)
if [ "$ACTUAL_SHA256" != "$EXPECTED_WHEEL_SHA256" ]; then
    echo "ERROR: Wheel SHA-256 mismatch" >&2
    echo "  Expected: $EXPECTED_WHEEL_SHA256" >&2
    echo "  Actual:   $ACTUAL_SHA256" >&2
    exit 1
fi

echo "[solve.sh] Installing pyperf from pre-built wheel..."
pip install --no-index --no-deps "$WHEEL_FILE"

echo "[solve.sh] Verifying installation..."
python3 -c "import pyperf; print(f'pyperf version: {pyperf.__version__}')"

echo "[solve.sh] Oracle solution installed successfully"
