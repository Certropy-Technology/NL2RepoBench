#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/parso
cat > /workspace/parso/__init__.py << 'OVERSIZED'
"""Oversized output implementation"""
__version__ = "0.8.7"

class FakeNode:
    def __init__(self):
        self._type = "node"
    
    @property
    def type(self):
        # Generate large output
        import sys
        for i in range(100000):
            print(f"Line {i}: " + "x" * 100, file=sys.stderr)
        return self._type
    
    @property
    def children(self):
        return []
    
    def get_code(self):
        return ""

class Module(FakeNode):
    pass

def parse(code, **kwargs):
    return Module()
OVERSIZED

cat > /workspace/setup.py << 'SETUP'
from setuptools import setup, find_packages
setup(
    name="parso",
    version="0.8.7",
    packages=find_packages(),
)
SETUP

python -m pip install --no-build-isolation --no-deps --no-index -e /workspace
