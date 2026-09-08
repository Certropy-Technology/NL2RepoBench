#!/bin/bash
set -euo pipefail

echo "[control:panic] Creating package that panics on import"

cd /workspace

# Create setup.py
cat > setup.py << 'SETUP'
from setuptools import setup

setup(
    name="dpath",
    version="2.2.0",
    description="Panic implementation",
    packages=["dpath"],
    python_requires=">=3.7",
)
SETUP

# Create dpath package
mkdir -p dpath

# Create __init__.py that crashes on import
cat > dpath/__init__.py << 'INIT'
"""Panic implementation - crashes on import."""

# Crash immediately on import
raise RuntimeError("Panic: intentional crash on import")
INIT

echo "[control:panic] Created package that crashes on import"
