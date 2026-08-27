#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
mkdir -p /workspace/aiobotocore
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"
[project]
name = "aiobotocore"
version = "0.0.0"
[tool.setuptools]
packages = ["aiobotocore"]
TOML
cat > /workspace/aiobotocore/__init__.py <<'PY'
__version__ = "0.0.0"
PY
