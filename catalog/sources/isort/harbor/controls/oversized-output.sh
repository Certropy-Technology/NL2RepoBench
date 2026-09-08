#!/bin/bash
set -euo pipefail

echo "=== Oversized Output Control: Package that floods output on import ==="

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

# Create package that floods stderr on import
cat > /workspace/isort/__init__.py << 'EOFINIT'
import sys

# Flood stderr with massive output
for i in range(100000):
    print(f"OVERSIZED OUTPUT LINE {i}: " + "X" * 500, file=sys.stderr)

__version__ = "9.0.1"
EOFINIT

cd /workspace
python -m pip install --no-build-isolation --no-deps --no-index -e .

echo "=== Oversized output control installed ==="
