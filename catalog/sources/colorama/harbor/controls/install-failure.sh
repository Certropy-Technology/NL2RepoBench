#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="/workspace"
mkdir -p "${WORKSPACE}"
cat > "${WORKSPACE}/pyproject.toml" << 'PYPROJ'
[build-system]
requires = ["nonexistent-backend-package==999"]
build-backend = "nonexistent.backend"
[project]
name = "colorama"
version = "0.4.6"
PYPROJ
