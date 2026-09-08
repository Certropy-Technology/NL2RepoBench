#!/bin/bash
set -euo pipefail
echo "[control:panic] Creating package that raises on import"
cd /workspace
cat > pyproject.toml << 'PYPROJECT'
[build-system]
requires = ["setuptools>=70"]
build-backend = "setuptools.build_meta"

[project]
name = "typer"
version = "0.0.0"
description = "Panic control"

[tool.setuptools]
packages = ["typer"]
PYPROJECT
mkdir -p typer
cat > typer/__init__.py << 'INIT'
raise RuntimeError("panic control: import always fails")
INIT
echo "[control:panic] Done"
