#!/bin/bash
set -euo pipefail

# Create implementation that crashes during import
mkdir -p /workspace/humanfriendly

cat > /workspace/humanfriendly/__init__.py << 'PANIC_INIT'
__version__ = '10.0'

# Panic: crash during module import
import sys
sys.exit(42)

class InvalidSize(Exception):
    pass
PANIC_INIT

cat > /workspace/setup.py << 'PANIC_SETUP'
from setuptools import setup, find_packages

setup(
    name='humanfriendly',
    version='10.0',
    packages=find_packages(),
)
PANIC_SETUP

cd /workspace
python -m pip install --no-build-isolation --no-deps --no-index -e .

echo "Panic implementation installed"
