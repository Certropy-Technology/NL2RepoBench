#!/bin/bash
# oversized-output control - floods stderr on import
set -euo pipefail

mkdir -p /workspace/deepdiff
cat > /workspace/deepdiff/__init__.py << 'OVERSIZED_EOF'
"""Oversized output - floods stderr"""
import sys

# Flood stderr with large output
for i in range(100000):
    print(f"WARNING: Line {i} - This is a very long warning message with lots of text to create oversized output" * 10, file=sys.stderr)

class DeepDiff:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Oversized")
    def to_dict(self):
        raise NotImplementedError("Oversized")

class DeepSearch:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Oversized")

class DeepHash:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Oversized")

class Delta:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Oversized")

def extract(*args, **kwargs):
    raise NotImplementedError("Oversized")

def parse_path(*args, **kwargs):
    raise NotImplementedError("Oversized")

def grep(*args, **kwargs):
    raise NotImplementedError("Oversized")

__all__ = ['DeepDiff', 'DeepSearch', 'DeepHash', 'Delta', 'extract', 'parse_path', 'grep']
OVERSIZED_EOF

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
echo "Oversized-output installed"
