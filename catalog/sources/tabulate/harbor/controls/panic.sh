#!/bin/bash
set -euo pipefail
echo "[control:panic] package raises on import"
cd /workspace
cat > pyproject.toml << 'PYPROJECT'
[build-system]
requires = ["setuptools>=70"]
build-backend = "setuptools.build_meta"
[project]
name = "tabulate"
version = "0.0.0"
[tool.setuptools]
packages = ["tabulate"]
PYPROJECT
mkdir -p tabulate
cat > tabulate/__init__.py << 'INIT'
raise RuntimeError("panic control: import always fails")
INIT
