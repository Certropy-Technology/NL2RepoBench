#!/bin/bash
set -euo pipefail

# Create stub implementation that raises NotImplementedError
mkdir -p /workspace/src/binaryornot

cat > /workspace/src/binaryornot/__init__.py << 'INIT'
"""Stub implementation"""
INIT

cat > /workspace/src/binaryornot/check.py << 'CHECK'
"""Stub implementation"""
def is_binary(filename, *, check_extensions=True):
    raise NotImplementedError("Stub implementation")
CHECK

cat > /workspace/src/binaryornot/helpers.py << 'HELPERS'
"""Stub implementation"""
def is_binary_string(bytes_to_check):
    raise NotImplementedError("Stub implementation")

def has_binary_extension(filename):
    raise NotImplementedError("Stub implementation")

def get_starting_chunk(filename, length=512):
    raise NotImplementedError("Stub implementation")
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
