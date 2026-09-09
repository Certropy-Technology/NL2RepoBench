#!/bin/bash
set -euo pipefail

# Create implementation that spawns background processes
mkdir -p /workspace/src/binaryornot

cat > /workspace/src/binaryornot/__init__.py << 'INIT'
"""Background process implementation"""
INIT

cat > /workspace/src/binaryornot/check.py << 'CHECK'
"""Background process implementation"""
import subprocess
import time

def is_binary(filename, *, check_extensions=True):
    # Spawn background process
    subprocess.Popen(['sleep', '3600'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.1)
    raise NotImplementedError("Background process")
CHECK

cat > /workspace/src/binaryornot/helpers.py << 'HELPERS'
"""Background process implementation"""
def is_binary_string(bytes_to_check):
    raise NotImplementedError("Background process")

def has_binary_extension(filename):
    raise NotImplementedError("Background process")

def get_starting_chunk(filename, length=512):
    raise NotImplementedError("Background process")
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
