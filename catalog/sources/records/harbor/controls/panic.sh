#!/bin/bash
set -euo pipefail

echo "[control:panic] Creating package that panics immediately on import"

cd /workspace

# Create setup.py
cat > setup.py << 'SETUP'
from setuptools import setup

setup(
    name="records",
    version="0.6.0",
    py_modules=["records"],
    install_requires=[],
)
SETUP

# Create records.py that panics on import
cat > records.py << 'RECORDS'
"""Panic implementation that crashes on import."""

# Panic immediately
raise RuntimeError("PANIC: Immediate crash on import")
RECORDS

echo "[control:panic] Panic package created"
