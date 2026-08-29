#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/pycparser
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
cat > /workspace/pycparser/__init__.py <<'PY'
import time
time.sleep(30)
PY
