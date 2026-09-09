#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/parso
cat > /workspace/parso/__init__.py << 'PANIC'
"""Panic implementation that crashes"""
__version__ = "0.8.7"

def parse(code, **kwargs):
    """Crashes immediately"""
    raise RuntimeError("Panic: intentional crash")
PANIC

cat > /workspace/setup.py << 'SETUP'
from setuptools import setup, find_packages
setup(
    name="parso",
    version="0.8.7",
    packages=find_packages(),
)
SETUP

python -m pip install --no-build-isolation --no-deps --no-index -e /workspace
