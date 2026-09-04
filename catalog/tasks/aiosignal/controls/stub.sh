#!/usr/bin/env bash
set -euo pipefail
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools==84.0.0"]
build-backend = "setuptools.build_meta"
[project]
name = "aiosignal"
version = "1.4.0"
[tool.setuptools]
packages = ["aiosignal"]
TOML
mkdir -p /workspace/aiosignal
printf "__version__ = '1.4.0'\nclass Signal(list):\n    pass\n" > /workspace/aiosignal/__init__.py
