#!/bin/bash
set -euo pipefail

echo "[control:install-failure] Creating invalid pyproject.toml to cause installation failure"

cd /workspace

# Create invalid TOML (missing closing bracket)
cat > pyproject.toml << 'PYPROJECT'
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "python-box"
version = "7.4.1"
description = "Invalid TOML
PYPROJECT

mkdir -p box
touch box/__init__.py

echo "[control:install-failure] Invalid pyproject.toml created"
