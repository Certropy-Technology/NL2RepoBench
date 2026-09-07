#!/bin/bash
set -euo pipefail

# Oracle for croniter task
# Source: https://github.com/kiorky/croniter
# Revision: 9181ba7de0a91512cb77d537b7e23631ffe4f7e8
# Expected digest: sha256:ac8e9d432017f5ef6c70f8660e98359353201d58383c38358c221378b74fbe77

echo "[Oracle] Starting croniter Oracle"
echo "[Oracle] Source digest: sha256:ac8e9d432017f5ef6c70f8660e98359353201d58383c38358c221378b74fbe77"

# Extract and verify source
if [ ! -f /solution/source.tar.gz ]; then
    echo "[Oracle] ERROR: source.tar.gz not found"
    exit 1
fi

cd /solution
tar -xzf source.tar.gz
cd croniter-*

# Verify source digest
ACTUAL_DIGEST=$(tar -czf - . | sha256sum | cut -d' ' -f1)
EXPECTED_DIGEST="ac8e9d432017f5ef6c70f8660e98359353201d58383c38358c221378b74fbe77"

if [ "$ACTUAL_DIGEST" != "$EXPECTED_DIGEST" ]; then
    echo "[Oracle] ERROR: Source digest mismatch"
    echo "[Oracle] Expected: $EXPECTED_DIGEST"
    echo "[Oracle] Actual: $ACTUAL_DIGEST"
    exit 1
fi

echo "[Oracle] Source digest verified"

# Install to workspace with --no-build-isolation
echo "[Oracle] Installing to /workspace with --no-build-isolation"
python -m pip install --no-build-isolation --no-deps --no-index -e . --prefix /workspace --no-warn-script-location

echo "[Oracle] Installation complete"
ls -la /workspace/lib/python*/site-packages/ || true

echo "[Oracle] Oracle setup complete"
