#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="/workspace"
mkdir -p "${WORKSPACE}/colorama"
cat > "${WORKSPACE}/colorama/__init__.py" << 'PY'
__version__ = "0.4.6"
# Generate large output to exceed limits
import sys
for i in range(50000):
    print("X" * 1000, file=sys.stderr)
PY
cat > "${WORKSPACE}/pyproject.toml" << 'PYPROJ'
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
[project]
name = "colorama"
version = "0.4.6"
PYPROJ
