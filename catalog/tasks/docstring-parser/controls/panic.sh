#!/bin/bash
set -euo pipefail
echo "[control:panic] Creating package that raises on import"
cd /workspace
cat > pyproject.toml << 'PYPROJECT'
[build-system]
requires = ["setuptools>=70"]
build-backend = "setuptools.build_meta"

[project]
name = "docstring_parser"
version = "0.0.0"
description = "Panic control"

[tool.setuptools]
packages = ["docstring_parser"]
PYPROJECT
mkdir -p docstring_parser
cat > docstring_parser/__init__.py << 'INIT'
raise RuntimeError("panic control: import always fails")
INIT
echo "[control:panic] Done"
