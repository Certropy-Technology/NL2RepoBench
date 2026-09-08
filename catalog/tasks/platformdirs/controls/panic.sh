#!/bin/bash
set -euo pipefail

echo "[control:panic] Creating package that panics on import"

cd /workspace
rm -rf /workspace/*

# Create pyproject.toml
cat > pyproject.toml << 'PYPROJECT'
[build-system]
build-backend = "hatchling.build"
requires = ["hatchling>=1.29"]

[project]
name = "platformdirs"
version = "4.11.3"
PYPROJECT

mkdir -p src/platformdirs

# Create __init__.py that crashes immediately
cat > src/platformdirs/__init__.py << 'INIT'
"""Package that panics on import."""
raise RuntimeError("Panic: immediate failure on import")
INIT

touch src/platformdirs/py.typed

echo "[control:panic] Created package that raises RuntimeError on import"
