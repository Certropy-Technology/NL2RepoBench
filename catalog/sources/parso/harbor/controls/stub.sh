#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/parso
cat > /workspace/parso/__init__.py << 'STUB'
"""Stub implementation of parso"""
__version__ = "0.8.7"

class Module:
    def __init__(self):
        raise NotImplementedError("Stub implementation")
    
    @property
    def children(self):
        raise NotImplementedError("Stub implementation")

class PythonNode:
    def __init__(self):
        raise NotImplementedError("Stub implementation")
    
    @property
    def type(self):
        raise NotImplementedError("Stub implementation")
    
    @property
    def children(self):
        raise NotImplementedError("Stub implementation")
    
    def get_code(self):
        raise NotImplementedError("Stub implementation")

def parse(code, **kwargs):
    """Stub parse function"""
    raise NotImplementedError("Stub implementation")
STUB

cat > /workspace/setup.py << 'SETUP'
from setuptools import setup, find_packages
setup(
    name="parso",
    version="0.8.7",
    packages=find_packages(),
)
SETUP

python -m pip install --no-build-isolation --no-deps --no-index -e /workspace
