#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
mkdir -p /workspace/fsspec
printf '__version__ = "0.0.0"\n__all__ = []\n' > /workspace/fsspec/__init__.py
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools==84.0.0"]
build-backend = "setuptools.build_meta"
[project]
name = "fsspec"
version = "0.0.0"
[tool.setuptools.packages.find]
include = ["fsspec*"]
EOF
