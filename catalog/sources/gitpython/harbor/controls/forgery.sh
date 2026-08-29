#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools==84.0.0"]
build-backend = "setuptools.build_meta"
[project]
name = "GitPython"
version = "3.1.60"
[tool.setuptools]
packages = ["git"]
TOML
mkdir -p /workspace/git
printf '%s\n' 'raise RuntimeError("forgery")' > /workspace/git/__init__.py
