#!/usr/bin/env bash
set -euo pipefail

# Create malformed package that fails to install
mkdir -p /workspace/dill

cat > /workspace/dill/__init__.py << 'BROKEN_INIT'
# Syntax error to break installation
def broken function(
BROKEN_INIT

cat > /workspace/setup.py << 'BROKEN_SETUP'
from setuptools import setup

setup(
    name="dill",
    version="0.4.1",
    packages=["dill"],
)
BROKEN_SETUP

# Attempt install (should fail)
cd /workspace
python -m pip install --no-build-isolation --no-deps --no-index -e . || true
echo "Install failure control executed"
