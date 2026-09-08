#!/bin/bash
set -euo pipefail

echo "[control:oversized-output] Creating package that floods output on import"

cd /workspace

cat > setup.py << 'SETUP'
#!/usr/bin/env python
from setuptools import setup

setup(
    name='trafaret',
    version='2.1.1',
    description='Oversized output control',
    packages=['trafaret'],
    python_requires='>=3.6',
)
SETUP

mkdir -p trafaret

cat > trafaret/__init__.py << 'INIT'
"""Floods stderr with large output on import."""
import sys

# Generate large output to stderr
for i in range(100000):
    print(f"OVERSIZED_OUTPUT_{i}: {'x' * 100}", file=sys.stderr)

__VERSION__ = (2, 1, 1)
INIT

echo "[control:oversized-output] Oversized output implementation created"
