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

# Create panic package that raises on import
cat > src/validators/__init__.py << 'INIT'
"""Panic package - raises on import."""
raise RuntimeError("Panic: Import failed intentionally")
INIT

# Install panic package
python -m pip install --no-build-isolation --no-deps --no-index -e .
echo "Panic package installed (will fail on import)"
