#!/bin/bash
set -euo pipefail

echo "[control:panic] Creating package that panics on import"

cd /workspace

# Create setup.py
cat > setup.py << 'SETUP'
from setuptools import setup, find_packages

setup(
    name='astor',
    version='0.8.1',
    description='Panic control',
    author='Panic',
    author_email='panic@example.com',
    license='BSD-3-Clause',
    packages=find_packages(),
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
)
SETUP

# Create astor package
mkdir -p astor

# Create VERSION file
echo "0.8.1" > astor/VERSION

# Create __init__.py that exits immediately on import
cat > astor/__init__.py << 'INIT'
"""Panic on import."""
import sys
print("PANIC: Exiting immediately", file=sys.stderr)
sys.exit(1)
INIT

echo "[control:panic] Panic implementation created"
