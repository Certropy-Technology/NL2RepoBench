#!/bin/bash
set -euo pipefail

echo "[control:install-failure] Creating package with broken installation"

cd /workspace

# Create invalid pyproject.toml
cat > pyproject.toml << 'PYPROJECT'
[tool.poetry]
name = "shortuuid"
version = "1.0.13"
# Missing required fields and invalid syntax
this is not valid toml !!!
PYPROJECT

echo "[control:install-failure] Created invalid pyproject.toml"
