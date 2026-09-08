#!/bin/bash
set -euo pipefail

echo "[control:panic] Creating package that raises on import"

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
# more-itertools panic
README

mkdir -p more_itertools
cat > more_itertools/__init__.py << 'INIT'
"""Panic control - raises on import."""
raise RuntimeError("Panic control: import raises immediately")
INIT

echo "[control:panic] Created package that raises on import"
