#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/importlib_metadata
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools==84.0.0"]
build-backend = "setuptools.build_meta"

[project]
name = "importlib_metadata"
version = "8.9.1.dev28+g9757b400e"
dependencies = ["zipp>=3.20"]
TOML
cat > /workspace/importlib_metadata/__init__.py <<'PY'
__all__ = []
PY
