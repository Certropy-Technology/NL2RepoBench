#!/bin/bash
set -euo pipefail
echo "[control:oversized-output] Creating package that floods stdout/stderr"
cd /workspace
cat > pyproject.toml << 'PYPROJECT'
[build-system]
requires = ["setuptools>=70"]
build-backend = "setuptools.build_meta"

[project]
name = "icecream"
version = "0.0.0"
description = "Oversized output control"

[tool.setuptools]
packages = ["icecream"]
PYPROJECT
mkdir -p icecream
cat > icecream/__init__.py << 'INIT'
import sys
for _ in range(100000):
    print("X" * 100, file=sys.stderr)
INIT
echo "[control:oversized-output] Done"
