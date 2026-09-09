#!/bin/bash
set -euo pipefail

# Create implementation that crashes when imported
mkdir -p /workspace/arrow
cat > /workspace/arrow/__init__.py << 'PANIC_INIT'
"""Panic implementation that crashes."""
__version__ = "1.4.0"

# Immediate crash on import
raise RuntimeError("Panic control: immediate crash")
PANIC_INIT

cat > /workspace/setup.py << 'SETUP_PY'
from setuptools import setup, find_packages

setup(
    name="arrow",
    version="1.4.0",
    packages=find_packages(),
    install_requires=[],
)
SETUP_PY

cd /workspace
python -m pip install --no-deps --no-index -e .
