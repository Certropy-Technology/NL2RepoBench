#!/usr/bin/env bash
set -euo pipefail

EXPECTED_REVISION="1ddce552cd1bdac5db3df931ba3df3bf9dac284c"
EXPECTED_DIGEST="sha256:27229586afe96571e8884a1f16170059cb08a43e05a9ff25241c1f8499ef9db6"

echo "Extracting source archive..."
tar -xzf source.tar.gz

cd python-json-patch-${EXPECTED_REVISION}

ACTUAL_REVISION=$(git rev-parse HEAD 2>/dev/null || echo "")
if [[ "$ACTUAL_REVISION" != "$EXPECTED_REVISION" ]]; then
    echo "ERROR: Revision mismatch. Expected: $EXPECTED_REVISION, Got: $ACTUAL_REVISION"
    exit 1
fi

# Verify source digest
cd ..
ACTUAL_DIGEST=$(sha256sum source.tar.gz | cut -d' ' -f1)
if [[ "sha256:$ACTUAL_DIGEST" != "$EXPECTED_DIGEST" ]]; then
    echo "ERROR: Source digest mismatch. Expected: $EXPECTED_DIGEST, Got: sha256:$ACTUAL_DIGEST"
    exit 1
fi

echo "Source verification passed. Installing to /workspace..."
cd python-json-patch-${EXPECTED_REVISION}
pip install --no-build-isolation --no-deps -e /workspace

echo "Oracle installation complete."
