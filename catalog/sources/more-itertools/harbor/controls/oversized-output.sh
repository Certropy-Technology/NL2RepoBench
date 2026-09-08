#!/bin/bash
set -euo pipefail

echo "[control:oversized-output] Creating package that floods stderr on import"

cd /workspace

cat > pyproject.toml << 'PYPROJECT'
[project]
name = "more-itertools"
version = "11.1.0"
description = "More routines for operating on iterables, beyond itertools"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}

[build-system]
requires = ["flit_core >=3.2,<4"]
build-backend = "flit_core.buildapi"
PYPROJECT

cat > README.md << 'README'
# more-itertools oversized-output
README

mkdir -p more_itertools
cat > more_itertools/__init__.py << 'INIT'
"""Oversized-output control - floods stderr on import."""
import sys

__version__ = "11.1.0"

# Flood stderr with large output
for i in range(100000):
    print(f"OVERSIZED OUTPUT LINE {i}: " + "X" * 1000, file=sys.stderr)
INIT

echo "[control:oversized-output] Created package that floods stderr"
