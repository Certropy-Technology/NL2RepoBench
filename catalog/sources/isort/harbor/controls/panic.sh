#!/bin/bash
set -euo pipefail

echo "=== Panic Control: Package that crashes on import ==="

mkdir -p /workspace/isort

cat > /workspace/pyproject.toml << 'EOFPYPROJECT'
[project]
name = "isort"
version = "9.0.1"
requires-python = ">=3.10.0"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
EOFPYPROJECT

# Create package that raises on import
cat > /workspace/isort/__init__.py << 'EOFINIT'
raise RuntimeError("Panic control: immediate crash on import")
EOFINIT

cd /workspace
python -m pip install --no-build-isolation --no-deps --no-index -e .

echo "=== Panic control installed (will crash on import) ==="
