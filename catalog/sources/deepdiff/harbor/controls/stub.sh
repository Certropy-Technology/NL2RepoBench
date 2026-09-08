#!/bin/bash
# stub control - functions exist but raise NotImplementedError
set -euo pipefail

mkdir -p /workspace/deepdiff
cat > /workspace/deepdiff/__init__.py << 'STUB_EOF'
"""Stub implementation of deepdiff"""

class DeepDiff:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Stub implementation")
    
    def to_dict(self):
        raise NotImplementedError("Stub implementation")

class DeepSearch:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Stub implementation")

class DeepHash:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Stub implementation")

class Delta:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Stub implementation")

def extract(*args, **kwargs):
    raise NotImplementedError("Stub implementation")

def parse_path(*args, **kwargs):
    raise NotImplementedError("Stub implementation")

def grep(*args, **kwargs):
    raise NotImplementedError("Stub implementation")

__all__ = ['DeepDiff', 'DeepSearch', 'DeepHash', 'Delta', 'extract', 'parse_path', 'grep']
STUB_EOF

cat > /workspace/setup.py << 'SETUP_EOF'
from setuptools import setup, find_packages

setup(
    name="deepdiff",
    version="9.1.0",
    packages=find_packages(),
    python_requires=">=3.10",
)
SETUP_EOF

cd /workspace
python3 -m pip install --no-build-isolation --no-deps --no-index -e . > /dev/null 2>&1
echo "Stub installed"
