#!/bin/bash
set -euo pipefail
echo "[control:oversized-output] package floods stderr on import"
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
import sys
for _ in range(100000):
    print("X" * 100, file=sys.stderr)
INIT
