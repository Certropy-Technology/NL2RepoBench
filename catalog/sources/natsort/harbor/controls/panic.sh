#!/bin/bash
set -euo pipefail

echo "[control:panic] Creating implementation that raises on import"

cd /workspace

# Create setup.py
cat > setup.py << 'SETUP'
from setuptools import setup, find_packages

setup(
    name="natsort",
    version="8.4.0",
    description="Panic implementation",
    packages=find_packages(),
    python_requires=">=3.7",
)
SETUP

# Create natsort package
mkdir -p natsort

# Create __init__.py that raises on import
cat > natsort/__init__.py << 'INIT'
"""Panic implementation that raises on import."""
raise RuntimeError("Panic! This package cannot be imported.")
INIT

echo "[control:panic] Panic implementation created"
echo "[control:panic] Package will raise RuntimeError on import"
