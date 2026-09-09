#!/usr/bin/env bash
set -euo pipefail

# Create package that panics/crashes when imported
mkdir -p /workspace/dill

cat > /workspace/dill/__init__.py << 'PANIC_INIT'
"""Panic module - crashes immediately"""
import sys
sys.exit(1)
PANIC_INIT

cat > /workspace/setup.py << 'PANIC_SETUP'
from setuptools import setup

setup(
    name="dill",
    version="0.4.1",
    packages=["dill"],
)
PANIC_SETUP

# Install
cd /workspace
python -m pip install --no-build-isolation --no-deps --no-index -e .
echo "Panic control installed"
