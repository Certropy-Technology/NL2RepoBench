#!/bin/bash
set -euo pipefail

echo "=== Install Failure Control: Creating invalid package ==="

mkdir -p /workspace/isort

# Create INVALID pyproject.toml (syntax error at end)
cat > /workspace/pyproject.toml << 'EOFPYPROJECT'
[project]
name = "isort"
version = "9.0.1"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
this is invalid toml syntax
EOFPYPROJECT

cat > /workspace/isort/__init__.py << 'EOFINIT'
__version__ = "9.0.1"
EOFINIT

cd /workspace
# This should fail due to invalid pyproject.toml
python -m pip install --no-build-isolation --no-deps --no-index -e . || true

echo "=== Install intentionally failed ==="
exit 1
