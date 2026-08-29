#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/pycparser
printf '%s\n' 'from .c_parser import CParser' > /workspace/pycparser/__init__.py
printf '%s\n' 'class CParser: pass' > /workspace/pycparser/c_parser.py
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools==80.9.0"]
build-backend = "setuptools.build_meta"
[project]
name = "pycparser"
version = "3.00"
[tool.setuptools]
packages = ["pycparser"]
TOML
