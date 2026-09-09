#!/bin/bash
set -euo pipefail

# Create implementation that panics/crashes on import
mkdir -p /workspace/src/binaryornot

cat > /workspace/src/binaryornot/__init__.py << 'INIT'
"""Panic implementation"""
import sys
sys.exit(42)
INIT

cat > /workspace/src/binaryornot/check.py << 'CHECK'
"""Panic implementation"""
raise RuntimeError("Panic!")
CHECK

cat > /workspace/src/binaryornot/helpers.py << 'HELPERS'
"""Panic implementation"""
raise RuntimeError("Panic!")
HELPERS

cat > /workspace/pyproject.toml << 'PYPROJECT'
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "binaryornot"
version = "0.6.0"
PYPROJECT

cd /workspace
python -m pip install --no-build-isolation --no-deps --no-index -e .
