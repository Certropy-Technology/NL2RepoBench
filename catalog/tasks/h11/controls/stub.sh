#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/h11
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools>=75", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "h11"
version = "0.0.0"
requires-python = ">=3.8"
dependencies = []
TOML
cat > /workspace/h11/__init__.py <<'PY'
__version__ = "0.0.0"
PY
