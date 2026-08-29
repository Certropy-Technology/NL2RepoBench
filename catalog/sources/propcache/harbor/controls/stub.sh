#!/usr/bin/env bash
set -euo pipefail
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools==80.9.0"]
build-backend = "setuptools.build_meta"
[project]
name = "propcache"
version = "0.0.0"
[tool.setuptools]
packages = ["propcache"]
TOML
mkdir -p /workspace/propcache
printf '__version__ = "0.0.0"\n' > /workspace/propcache/__init__.py
