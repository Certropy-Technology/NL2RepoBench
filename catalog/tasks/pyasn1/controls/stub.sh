#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/pyasn1
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"
[project]
name = "pyasn1"
version = "0.0.0"
[tool.setuptools]
packages = ["pyasn1"]
TOML
cat > /workspace/pyasn1/__init__.py <<'PY'
__version__ = "0.0.0"
PY
