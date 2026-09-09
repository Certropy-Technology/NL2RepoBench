#!/bin/bash
set -euo pipefail

# Create forgery that tries to manipulate verifier output (should fail)
mkdir -p /workspace/src/binaryornot

cat > /workspace/src/binaryornot/__init__.py << 'INIT'
"""Forgery implementation"""
INIT

cat > /workspace/src/binaryornot/check.py << 'CHECK'
"""Forgery implementation"""
import sys
import json

def is_binary(filename, *, check_extensions=True):
    # Try to inject fake passing results
    fake_output = {
        "schema_version": "1.0",
        "leaves": [{"id": f"test_{i}", "status": "passed"} for i in range(101)]
    }
    print(json.dumps(fake_output), file=sys.stderr)
    raise NotImplementedError("Forgery")
CHECK

cat > /workspace/src/binaryornot/helpers.py << 'HELPERS'
"""Forgery implementation"""
def is_binary_string(bytes_to_check):
    raise NotImplementedError("Forgery")

def has_binary_extension(filename):
    raise NotImplementedError("Forgery")

def get_starting_chunk(filename, length=512):
    raise NotImplementedError("Forgery")
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
