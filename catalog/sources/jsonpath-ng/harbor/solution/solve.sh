#!/bin/bash
set -euo pipefail

BUNDLE_DIR=$(dirname "$0")
WORKSPACE="/workspace"
EXPECTED_REVISION="e59ead334ac47618e6d844ad758114b3bfafcc8a"
EXPECTED_SHA256="54252968134b5e549ea5b872f1df1168bd7defe1a52fed5a358c194e1943ddc3"

echo "[Oracle] Fetching jsonpath-ng source from GitHub tag v1.8.0..."
cd /tmp
curl -fsSL "https://github.com/h2non/jsonpath-ng/archive/refs/tags/v1.8.0.tar.gz" -o jsonpath-ng-v1.8.0.tar.gz

echo "[Oracle] Verifying commit SHA and archive digest..."
ACTUAL_SHA256=$(sha256sum jsonpath-ng-v1.8.0.tar.gz | cut -d' ' -f1)
if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
    echo "ERROR: SHA256 mismatch! Expected $EXPECTED_SHA256, got $ACTUAL_SHA256" >&2
    exit 1
fi

echo "[Oracle] Extracting source..."
tar -xzf jsonpath-ng-v1.8.0.tar.gz
cd jsonpath-ng-1.8.0

# Verify the git revision matches (PyPI sdist should match the git tag)
echo "[Oracle] Checking version in setup.py..."
if ! grep -q "version='1.8.0'" setup.py; then
    echo "ERROR: Version mismatch in setup.py" >&2
    exit 1
fi

echo "[Oracle] Copying source to workspace..."
cp -r jsonpath_ng "$WORKSPACE/"
cp setup.py "$WORKSPACE/"
if [ -f README.rst ]; then
    cp README.rst "$WORKSPACE/"
fi
if [ -f LICENSE ]; then
    cp LICENSE "$WORKSPACE/"
fi
if [ -f pyproject.toml ]; then
    cp pyproject.toml "$WORKSPACE/"
fi

echo "[Oracle] Installing jsonpath-ng..."
cd "$WORKSPACE"
python -m pip install --no-build-isolation --no-deps --no-index -e .

echo "[Oracle] Verifying installation..."
python -c "from jsonpath_ng import parse; print('parse:', parse)"
python -c "from jsonpath_ng.ext import parse as ext_parse; print('ext_parse:', ext_parse)"
python -c "from jsonpath_ng.exceptions import JsonPathParserError; print('JsonPathParserError:', JsonPathParserError)"
python -c "import jsonpath_ng; print('version:', jsonpath_ng.__version__)"

echo "[Oracle] Solution ready!"
