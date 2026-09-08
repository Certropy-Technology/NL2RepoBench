#!/bin/bash
set -euo pipefail

echo "[control:panic] Creating implementation that crashes during test execution"

cd /workspace

# Create setup.py
cat > setup.py << 'SETUP'
from setuptools import setup

setup(
    name="Deprecated",
    version="1.3.1",
    packages=["deprecated"],
    install_requires=["wrapt>=1.10,<3"],
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
)
SETUP

# Create deprecated package
mkdir -p deprecated

# Create __init__.py that crashes on import
cat > deprecated/__init__.py << 'INIT'
"""Panic implementation that crashes."""
import sys

__version__ = "1.3.1"

# Cause a crash
sys.exit(1)
INIT

echo "[control:panic] Panic implementation created (crashes on import)"
