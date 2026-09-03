#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/xdist
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = []
build-backend = "setuptools.build_meta:__legacy__"
[project]
name = "pytest-xdist"
version = "0.0.0"
[tool.setuptools]
packages = ["xdist"]
TOML
printf '__version__ = "0.0.0"\n' > /workspace/xdist/__init__.py
