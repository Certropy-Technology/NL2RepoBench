#!/bin/bash
set -euo pipefail

# Create invalid package that fails to install
mkdir -p /workspace/src/binaryornot

cat > /workspace/pyproject.toml << 'PYPROJECT'
[build-system]
requires = ["nonexistent-build-backend-xyz123"]
build-backend = "nonexistent.build"

[project]
name = "binaryornot"
version = "0.6.0"
PYPROJECT

cd /workspace
python -m pip install --no-build-isolation --no-deps --no-index -e . || true
exit 1
