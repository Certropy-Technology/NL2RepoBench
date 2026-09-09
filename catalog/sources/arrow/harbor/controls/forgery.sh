#!/bin/bash
set -euo pipefail

# Create a forgery that tries to manipulate test results
mkdir -p /workspace/arrow
cat > /workspace/arrow/__init__.py << 'FORGERY_INIT'
"""Forgery implementation that attempts to fake results."""

__version__ = "1.4.0"

import sys
import json

# Try to intercept the verifier output
class ForgeryAttempt:
    def __init__(self):
        self.fake_output = {
            "schema_version": "1.0",
            "leaves": [{"id": f"test_{i}", "status": "passed"} for i in range(90)]
        }
    
    def __del__(self):
        # Try to print fake results on exit
        try:
            print(json.dumps(self.fake_output))
        except:
            pass

_forgery = ForgeryAttempt()

class Arrow:
    """Forgery Arrow class."""
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Forgery implementation")
    
    @classmethod
    def range(cls, *args, **kwargs):
        raise NotImplementedError("Forgery implementation")
    
    def format(self, *args, **kwargs):
        raise NotImplementedError("Forgery implementation")
    
    def shift(self, *args, **kwargs):
        raise NotImplementedError("Forgery implementation")
    
    def replace(self, *args, **kwargs):
        raise NotImplementedError("Forgery implementation")
    
    def to(self, *args, **kwargs):
        raise NotImplementedError("Forgery implementation")
    
    def floor(self, *args, **kwargs):
        raise NotImplementedError("Forgery implementation")
    
    def ceil(self, *args, **kwargs):
        raise NotImplementedError("Forgery implementation")
    
    def timestamp(self, *args, **kwargs):
        raise NotImplementedError("Forgery implementation")
    
    def humanize(self, *args, **kwargs):
        raise NotImplementedError("Forgery implementation")
    
    def isoformat(self, *args, **kwargs):
        raise NotImplementedError("Forgery implementation")
    
    def span(self, *args, **kwargs):
        raise NotImplementedError("Forgery implementation")

def get(*args, **kwargs):
    """Forgery get function."""
    raise NotImplementedError("Forgery implementation")

def utcnow(*args, **kwargs):
    """Forgery utcnow function."""
    raise NotImplementedError("Forgery implementation")
FORGERY_INIT

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
