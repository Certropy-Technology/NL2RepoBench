#!/bin/bash
set -euo pipefail

echo "[control:install-failure] Creating package with invalid configuration"

cd /workspace

# Create invalid pyproject.toml (malformed TOML)
cat > pyproject.toml << 'PYPROJECT'
[build-system
build-backend = "setuptools.build_meta"
requires = ["setuptools >= 77.0"

[project]
name = "dateparser
version = "1.4.3"
PYPROJECT

echo "[control:install-failure] Created invalid pyproject.toml"
