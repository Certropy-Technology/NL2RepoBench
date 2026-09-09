#!/bin/bash
set -euo pipefail

# Create implementation that produces oversized output
mkdir -p /workspace/arrow
cat > /workspace/arrow/__init__.py << 'OVERSIZED_INIT'
"""Oversized output implementation."""
__version__ = "1.4.0"

# Print large amount of data when any function is called
class Arrow:
    def __init__(self, *args, **kwargs):
        # Print 100KB of data
        print("X" * 102400)
        raise NotImplementedError("Oversized control")
    
    @classmethod
    def range(cls, *args, **kwargs):
        print("X" * 102400)
        raise NotImplementedError("Oversized control")
    
    def format(self, *args, **kwargs):
        print("X" * 102400)
        raise NotImplementedError("Oversized control")
    
    def shift(self, *args, **kwargs):
        print("X" * 102400)
        raise NotImplementedError("Oversized control")
    
    def replace(self, *args, **kwargs):
        print("X" * 102400)
        raise NotImplementedError("Oversized control")
    
    def to(self, *args, **kwargs):
        print("X" * 102400)
        raise NotImplementedError("Oversized control")
    
    def floor(self, *args, **kwargs):
        print("X" * 102400)
        raise NotImplementedError("Oversized control")
    
    def ceil(self, *args, **kwargs):
        print("X" * 102400)
        raise NotImplementedError("Oversized control")
    
    def timestamp(self, *args, **kwargs):
        print("X" * 102400)
        raise NotImplementedError("Oversized control")
    
    def humanize(self, *args, **kwargs):
        print("X" * 102400)
        raise NotImplementedError("Oversized control")
    
    def isoformat(self, *args, **kwargs):
        print("X" * 102400)
        raise NotImplementedError("Oversized control")
    
    def span(self, *args, **kwargs):
        print("X" * 102400)
        raise NotImplementedError("Oversized control")

def get(*args, **kwargs):
    print("X" * 102400)
    raise NotImplementedError("Oversized control")

def utcnow(*args, **kwargs):
    print("X" * 102400)
    raise NotImplementedError("Oversized control")
OVERSIZED_INIT

cat > /workspace/setup.py << 'SETUP_PY'
from setuptools import setup, find_packages

setup(
    name="arrow",
    version="1.4.0",
    packages=find_packages(),
    install_requires=[],
)
SETUP_PY

cd /workspace
python -m pip install --no-deps --no-index -e .
