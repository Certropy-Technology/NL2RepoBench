#!/usr/bin/env bash
set -euo pipefail

BUNDLE_DIR=$(dirname "$0")
EXPECTED_SHA256="1ea2b4fa678b8ca268253798d5963935df39132d47c3e241c0a0732224005e7d"
EXPECTED_REVISION="9f8a9f6b7479e8ee4d033976d0a24faaca4a1830"

cd "$BUNDLE_DIR"

if [ ! -f wcmatch-11.0.1.tar.gz ]; then
    echo "Error: wcmatch-11.0.1.tar.gz not found" >&2
    exit 1
fi

echo "Verifying archive SHA-256..."
ACTUAL_SHA256=$(sha256sum wcmatch-11.0.1.tar.gz | cut -d' ' -f1)
if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
    echo "Error: SHA-256 mismatch. Expected $EXPECTED_SHA256, got $ACTUAL_SHA256" >&2
    exit 1
fi

echo "Extracting to /workspace..."
tar -xzf wcmatch-11.0.1.tar.gz -C /workspace --strip-components=1

cd /workspace

echo "Installing wcmatch..."
python -m pip install --no-build-isolation --no-deps --no-index -e .

echo "Verifying installation..."
python -c "import wcmatch; import wcmatch.fnmatch; import wcmatch.glob; import wcmatch.pathlib; print('wcmatch version:', wcmatch.__version__)"

echo "Checking version..."
VERSION=$(python -c "import wcmatch; print(wcmatch.__version__)")
if [ "$VERSION" != "11.0.1" ]; then
    echo "Error: Version mismatch. Expected 11.0.1, got $VERSION" >&2
    exit 1
fi

echo "Oracle solution prepared successfully"
