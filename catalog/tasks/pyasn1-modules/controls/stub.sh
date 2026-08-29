#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/pyasn1_modules
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = []
build-backend = "setuptools.build_meta:__legacy__"
[project]
name = "pyasn1-modules"
version = "0.4.2"
[tool.setuptools]
packages = ["pyasn1_modules"]
TOML
cat > /workspace/pyasn1_modules/__init__.py <<'PY'
__version__ = "0.4.2"
PY
