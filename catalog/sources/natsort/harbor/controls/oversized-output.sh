#!/bin/bash
set -euo pipefail

echo "[control:oversized-output] Creating implementation that floods stderr on import"

cd /workspace

# Create setup.py
cat > setup.py << 'SETUP'
from setuptools import setup, find_packages

setup(
    name="natsort",
    version="8.4.0",
    description="Oversized output implementation",
    packages=find_packages(),
    python_requires=">=3.7",
)
SETUP

# Create natsort package
mkdir -p natsort

# Create __init__.py that floods stderr on import
cat > natsort/__init__.py << 'INIT'
"""Implementation that floods stderr on import."""
import sys

# Flood stderr with large output
for i in range(100000):
    print(f"[OVERSIZED] Line {i}: " + "X" * 1000, file=sys.stderr)

class ns:
    INT = I = 0
    FLOAT = F = 1

def natsorted(seq, key=None, reverse=False, alg=0, **kwargs):
    return sorted(seq, key=key, reverse=reverse)

__version__ = "8.4.0"
INIT

echo "[control:oversized-output] Oversized output implementation created"
echo "[control:oversized-output] Package will flood stderr with large output on import"
