#!/bin/bash
set -euo pipefail
echo "[control:install-failure] Creating package with broken installation"
cd /workspace
cat > pyproject.toml << 'PYPROJECT'
[build-system]
requires = ["setuptools>=70"]
build-backend = "setuptools.build_meta"

[project]
name = "docstring_parser"
version = "0.0.0"
# invalid toml below
this is not valid toml !!!
PYPROJECT
echo "[control:install-failure] Created invalid pyproject.toml"
