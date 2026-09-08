#!/bin/bash
set -euo pipefail

echo "[control:background-process] Creating package that spawns background processes on import"

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
# more-itertools background-process
README

mkdir -p more_itertools
cat > more_itertools/__init__.py << 'INIT'
"""Background-process control - spawns processes on import."""
import subprocess

__version__ = "11.1.0"

# Spawn 5 background processes
for i in range(5):
    subprocess.Popen(["sleep", "3600"])
INIT

echo "[control:background-process] Created package that spawns background processes"
