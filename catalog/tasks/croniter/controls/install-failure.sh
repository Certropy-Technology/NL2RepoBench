#!/bin/bash
set -euo pipefail

# Install failure control - broken package metadata
WORKSPACE="/workspace"

echo "[CONTROL:INSTALL-FAILURE] Creating broken installation"

mkdir -p "${WORKSPACE}/src/croniter"

# Create invalid pyproject.toml
cat > "${WORKSPACE}/pyproject.toml" << 'PYPROJECT'
[build-system]
requires = ["nonexistent-build-backend==999.999.999"]
build-backend = "nonexistent.backend"

[project]
name = "croniter"
version = "broken"
PYPROJECT

cat > "${WORKSPACE}/src/croniter/__init__.py" << 'INIT'
# This will never be reached due to build failure
pass
INIT

echo "[CONTROL:INSTALL-FAILURE] Broken package created"
