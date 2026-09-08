#!/bin/bash
set -euo pipefail

# Create broken package that fails to install
mkdir -p /workspace
cat > /workspace/toposort.py << 'BROKEN'
# Syntax error to break installation
def toposort(data
    pass
BROKEN

cd /workspace
cat > setup.py << 'SETUP'
from setuptools import setup
setup(
    name="toposort",
    version="1.10",
    py_modules=["toposort"],
)
SETUP

# This will fail due to syntax error during installation
python -m pip install --no-deps -e .
