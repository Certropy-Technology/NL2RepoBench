#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/tokenizers
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools==80.10.2"]
build-backend = "setuptools.build_meta"
[project]
name = "tokenizers"
version = "0.23.2.dev0"
[tool.setuptools]
packages = ["tokenizers"]
TOML
printf '__version__ = "0.23.2-dev.0"\n' > /workspace/tokenizers/__init__.py
