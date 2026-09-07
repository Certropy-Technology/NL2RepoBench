#!/bin/bash
set -euo pipefail

# Install-failure control for pyperf.
# Creates a package that will fail to install.

WORKSPACE="/workspace"
cd "${WORKSPACE}"

echo "[control:install-failure] Creating broken package" >&2

# Create invalid pyproject.toml with syntax error
cat > pyproject.toml << 'PYPROJECT'
[build-system
requires = ["setuptools >= 61"
build-backend = "setuptools.build_meta"

[project
name = "pyperf
version = "2.10.0"
PYPROJECT

echo "[control:install-failure] Broken package created" >&2
exit 0
