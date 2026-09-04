#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
mkdir -p /workspace/cffi
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools==84.0.0"]
build-backend = "setuptools.build_meta"
[project]
name = "cffi"
version = "2.2.0.dev0"
[tool.setuptools]
packages = ["cffi"]
TOML
printf 'while True: pass\n' > /workspace/cffi/__init__.py
