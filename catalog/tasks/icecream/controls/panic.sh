#!/bin/bash
set -euo pipefail
echo "[control:panic] Creating package that raises on import"
cd /workspace
cat > pyproject.toml << 'PYPROJECT'
[build-system]
requires = ["setuptools>=70"]
build-backend = "setuptools.build_meta"

[project]
name = "icecream"
version = "0.0.0"
description = "Panic control"

[tool.setuptools]
packages = ["icecream"]
PYPROJECT
mkdir -p icecream
cat > icecream/__init__.py << 'INIT'
raise RuntimeError("panic control: import always fails")
INIT
echo "[control:panic] Done"
