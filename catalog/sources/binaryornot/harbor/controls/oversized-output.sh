#!/bin/bash
set -euo pipefail

# Create implementation that produces huge output
mkdir -p /workspace/src/binaryornot

cat > /workspace/src/binaryornot/__init__.py << 'INIT'
"""Oversized output implementation"""
INIT

cat > /workspace/src/binaryornot/check.py << 'CHECK'
"""Oversized output implementation"""
def is_binary(filename, *, check_extensions=True):
    # Generate massive output
    import sys
    for i in range(1000000):
        print(f"Line {i}: {'X' * 1000}", file=sys.stderr)
    raise NotImplementedError("Oversized")
CHECK

cat > /workspace/src/binaryornot/helpers.py << 'HELPERS'
"""Oversized output implementation"""
def is_binary_string(bytes_to_check):
    raise NotImplementedError("Oversized")

def has_binary_extension(filename):
    raise NotImplementedError("Oversized")

def get_starting_chunk(filename, length=512):
    raise NotImplementedError("Oversized")
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
