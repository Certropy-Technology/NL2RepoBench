#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/parso
cat > /workspace/parso/__init__.py << 'BACKGROUND'
"""Background process implementation"""
__version__ = "0.8.7"
import subprocess
import sys

# Start a background process
subprocess.Popen([sys.executable, "-c", "import time; time.sleep(3600)"], 
                 stdout=subprocess.DEVNULL, 
                 stderr=subprocess.DEVNULL)

class FakeNode:
    def __init__(self):
        self._type = "node"
    
    @property
    def type(self):
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
BACKGROUND

cat > /workspace/setup.py << 'SETUP'
from setuptools import setup, find_packages
setup(
    name="parso",
    version="0.8.7",
    packages=find_packages(),
)
SETUP

python -m pip install --no-build-isolation --no-deps --no-index -e /workspace
