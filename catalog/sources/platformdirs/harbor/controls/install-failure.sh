#!/bin/bash
set -euo pipefail

echo "[control:install-failure] Creating package that will fail to install"

cd /workspace
rm -rf /workspace/*

# Create pyproject.toml with invalid backend
cat > pyproject.toml << 'PYPROJECT'
[build-system]
build-backend = "nonexistent.backend"
requires = ["nonexistent-package-xyz>=999.0"]

[project]
name = "platformdirs"
version = "4.11.3"
PYPROJECT

echo "[control:install-failure] Created package with nonexistent build backend"
