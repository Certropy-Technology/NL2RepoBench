#!/bin/bash
# Install failure control - intentionally fails installation
set -euo pipefail

WORKSPACE="/workspace"
mkdir -p "$WORKSPACE/jsonpath_ng"

cat > "$WORKSPACE/jsonpath_ng/__init__.py" << 'FAILPY'
# Syntax error to cause import failure
this is not valid python syntax !!!
FAILPY

cat > "$WORKSPACE/setup.py" << 'FAILSETUP'
from setuptools import setup, find_packages
setup(
    name='jsonpath-ng',
    version='1.8.0',
    packages=find_packages(),
)
FAILSETUP

cd "$WORKSPACE"
# This should fail
python -m pip install --no-build-isolation --no-deps --no-index -e . || {
    echo "[Control: install-failure] Installation failed as expected"
    exit 0
}

echo "[Control: install-failure] ERROR: Installation should have failed!"
exit 1
