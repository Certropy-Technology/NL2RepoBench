#!/bin/bash
set -euo pipefail

echo "[control:panic] Creating package that panics on import"

cd /workspace

cat > setup.py << 'SETUP'
#!/usr/bin/env python
from setuptools import setup

setup(
    name='trafaret',
    version='2.1.1',
    description='Panic control',
    packages=['trafaret'],
    python_requires='>=3.6',
)
SETUP

mkdir -p trafaret

cat > trafaret/__init__.py << 'INIT'
"""Panic on import."""
import sys
print("PANIC: Immediate exit on import", file=sys.stderr)
sys.exit(1)
INIT

echo "[control:panic] Panic implementation created - exits on import"
