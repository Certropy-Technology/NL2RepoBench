#!/bin/bash
set -euo pipefail

echo "[control:background-process] Creating implementation that spawns background processes"

cd /workspace

# Create setup.py
cat > setup.py << 'SETUP'
from setuptools import setup, find_packages

setup(
    name="natsort",
    version="8.4.0",
    description="Background process implementation",
    packages=find_packages(),
    python_requires=">=3.7",
)
SETUP

# Create natsort package
mkdir -p natsort

# Create __init__.py that spawns background processes on import
cat > natsort/__init__.py << 'INIT'
"""Implementation that spawns background processes."""
import subprocess
import sys

# Spawn 5 background sleep processes
for i in range(5):
    subprocess.Popen(['sleep', '3600'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

class ns:
    INT = I = 0
    FLOAT = F = 1

def natsorted(seq, key=None, reverse=False, alg=0, **kwargs):
    return sorted(seq, key=key, reverse=reverse)

__version__ = "8.4.0"
INIT

echo "[control:background-process] Background process implementation created"
echo "[control:background-process] Package will spawn 5 background sleep processes on import"
