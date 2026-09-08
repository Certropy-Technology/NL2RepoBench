#!/bin/bash
set -euo pipefail

echo "[control:install-failure] Creating package with broken installation"

cd /workspace

# Create invalid pyproject.toml
cat > pyproject.toml << 'PYPROJECT'
[project]
name = "phonenumbers"
version = "9.0.38"
# Invalid TOML syntax to cause installation failure
this is not valid toml syntax !!!
[invalid section without closing
PYPROJECT

echo "[control:install-failure] Created invalid pyproject.toml that will cause installation failure"
