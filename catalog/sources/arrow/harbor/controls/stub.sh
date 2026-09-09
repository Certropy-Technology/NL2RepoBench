#!/bin/bash
set -euo pipefail

# Create minimal stub implementation that raises NotImplementedError
mkdir -p /workspace/arrow
cat > /workspace/arrow/__init__.py << 'STUB_INIT'
"""Stub implementation of arrow."""

__version__ = "1.4.0"

class Arrow:
    """Stub Arrow class."""
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Stub implementation")
    
    @classmethod
    def range(cls, *args, **kwargs):
        raise NotImplementedError("Stub implementation")
    
    def format(self, *args, **kwargs):
        raise NotImplementedError("Stub implementation")
    
    def shift(self, *args, **kwargs):
        raise NotImplementedError("Stub implementation")
    
    def replace(self, *args, **kwargs):
        raise NotImplementedError("Stub implementation")
    
    def to(self, *args, **kwargs):
        raise NotImplementedError("Stub implementation")
    
    def floor(self, *args, **kwargs):
        raise NotImplementedError("Stub implementation")
    
    def ceil(self, *args, **kwargs):
        raise NotImplementedError("Stub implementation")
    
    def timestamp(self, *args, **kwargs):
        raise NotImplementedError("Stub implementation")
    
    def humanize(self, *args, **kwargs):
        raise NotImplementedError("Stub implementation")
    
    def isoformat(self, *args, **kwargs):
        raise NotImplementedError("Stub implementation")
    
    def span(self, *args, **kwargs):
        raise NotImplementedError("Stub implementation")

def get(*args, **kwargs):
    """Stub get function."""
    raise NotImplementedError("Stub implementation")

def utcnow(*args, **kwargs):
    """Stub utcnow function."""
    raise NotImplementedError("Stub implementation")
STUB_INIT

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
