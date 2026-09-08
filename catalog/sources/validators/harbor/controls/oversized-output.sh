#!/usr/bin/env bash
set -euo pipefail

cd /workspace

mkdir -p src/validators

cat > pyproject.toml << 'PYPROJECT'
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[project]
name = "validators"
version = "0.35.0"
requires-python = ">=3.9"
dependencies = []

[tool.setuptools.packages.find]
where = ["src"]
include = ["validators*"]
PYPROJECT

# Create package that floods stderr on import
cat > src/validators/__init__.py << 'INIT'
"""Oversized output package - floods stderr on import."""
import sys
for i in range(100000):
    print(f"Flooding stderr with line {i}: {'X' * 100}", file=sys.stderr)

__version__ = "0.35.0"
INIT

# Install oversized package
python -m pip install --no-build-isolation --no-deps --no-index -e .
echo "Oversized output package installed"
