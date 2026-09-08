#!/bin/bash
# background-process control - spawns background processes on import
set -euo pipefail

mkdir -p /workspace/deepdiff
cat > /workspace/deepdiff/__init__.py << 'BACKGROUND_EOF'
"""Background process - spawns processes on import"""
import subprocess
import time

# Spawn 5 background processes that sleep
for i in range(5):
    subprocess.Popen(['sleep', '3600'], start_new_session=True)

class DeepDiff:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Background")
    def to_dict(self):
        raise NotImplementedError("Background")

class DeepSearch:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Background")

class DeepHash:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Background")

class Delta:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Background")

def extract(*args, **kwargs):
    raise NotImplementedError("Background")

def parse_path(*args, **kwargs):
    raise NotImplementedError("Background")

def grep(*args, **kwargs):
    raise NotImplementedError("Background")

__all__ = ['DeepDiff', 'DeepSearch', 'DeepHash', 'Delta', 'extract', 'parse_path', 'grep']
BACKGROUND_EOF

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
echo "Background-process installed"
