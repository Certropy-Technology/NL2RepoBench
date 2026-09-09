#!/bin/bash
set -euo pipefail

# Create broken setup that will fail installation
mkdir -p /workspace/humanfriendly

cat > /workspace/humanfriendly/__init__.py << 'BROKEN_INIT'
# Syntax error: unclosed string
__version__ = '10.0
BROKEN_INIT

cat > /workspace/setup.py << 'BROKEN_SETUP'
from setuptools import setup, find_packages

setup(
    name='humanfriendly',
    version='10.0',
    packages=find_packages(),
)
BROKEN_SETUP

cd /workspace
# This will fail due to syntax error
python -m pip install --no-build-isolation --no-deps --no-index -e .

echo "This should not be reached"
