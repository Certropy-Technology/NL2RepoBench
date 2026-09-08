#!/bin/bash
# forgery control - returns plausible but incorrect results
set -euo pipefail

mkdir -p /workspace/deepdiff
cat > /workspace/deepdiff/__init__.py << 'FORGERY_EOF'
"""Forgery implementation - returns plausible but wrong results"""

class DeepDiff:
    def __init__(self, t1, t2, **kwargs):
        self.t1 = t1
        self.t2 = t2
        self.kwargs = kwargs
    
    def to_dict(self):
        # Always return empty dict (incorrect for most cases)
        return {}

class DeepSearch:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Forgery")

class DeepHash:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Forgery")

class Delta:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Forgery")

def extract(*args, **kwargs):
    raise NotImplementedError("Forgery")

def parse_path(*args, **kwargs):
    raise NotImplementedError("Forgery")

def grep(*args, **kwargs):
    raise NotImplementedError("Forgery")

__all__ = ['DeepDiff', 'DeepSearch', 'DeepHash', 'Delta', 'extract', 'parse_path', 'grep']
FORGERY_EOF

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
echo "Forgery installed"
