#!/bin/bash
# panic control - import raises exception
set -euo pipefail

mkdir -p /workspace/deepdiff
cat > /workspace/deepdiff/__init__.py << 'PANIC_EOF'
"""Panic implementation - raises on import"""
raise RuntimeError("Panic: module initialization failed")
PANIC_EOF

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
echo "Panic installed"
