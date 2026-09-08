#!/bin/bash
set -euo pipefail

echo "[control:background-process] Creating package that spawns background processes"

cd /workspace

cat > setup.py << 'SETUP'
#!/usr/bin/env python
from setuptools import setup

setup(
    name='trafaret',
    version='2.1.1',
    description='Background process control',
    packages=['trafaret'],
    python_requires='>=3.6',
)
SETUP

mkdir -p trafaret

cat > trafaret/__init__.py << 'INIT'
"""Spawns background processes on import."""
import subprocess
import sys

# Spawn multiple long-running background processes
for i in range(5):
    subprocess.Popen(
        [sys.executable, '-c', 'import time; time.sleep(3600)'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

__VERSION__ = (2, 1, 1)
INIT

echo "[control:background-process] Background process implementation created"
