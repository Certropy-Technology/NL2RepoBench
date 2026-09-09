#!/bin/bash
set -euo pipefail

# Create implementation that spawns background processes
mkdir -p /workspace/arrow
cat > /workspace/arrow/__init__.py << 'BACKGROUND_INIT'
"""Background process implementation."""
__version__ = "1.4.0"

import subprocess
import time

# Spawn background process on import
try:
    subprocess.Popen(
        ["sh", "-c", "sleep 300"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
except:
    pass

class Arrow:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Background process control")
    
    @classmethod
    def range(cls, *args, **kwargs):
        raise NotImplementedError("Background process control")
    
    def format(self, *args, **kwargs):
        raise NotImplementedError("Background process control")
    
    def shift(self, *args, **kwargs):
        raise NotImplementedError("Background process control")
    
    def replace(self, *args, **kwargs):
        raise NotImplementedError("Background process control")
    
    def to(self, *args, **kwargs):
        raise NotImplementedError("Background process control")
    
    def floor(self, *args, **kwargs):
        raise NotImplementedError("Background process control")
    
    def ceil(self, *args, **kwargs):
        raise NotImplementedError("Background process control")
    
    def timestamp(self, *args, **kwargs):
        raise NotImplementedError("Background process control")
    
    def humanize(self, *args, **kwargs):
        raise NotImplementedError("Background process control")
    
    def isoformat(self, *args, **kwargs):
        raise NotImplementedError("Background process control")
    
    def span(self, *args, **kwargs):
        raise NotImplementedError("Background process control")

def get(*args, **kwargs):
    raise NotImplementedError("Background process control")

def utcnow(*args, **kwargs):
    raise NotImplementedError("Background process control")
BACKGROUND_INIT

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
