#!/bin/bash
set -euo pipefail

echo "[control:background-process] Creating implementation that spawns background processes"

cd /workspace

cat > pyproject.toml << 'PYPROJECT'
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "python-box"
version = "7.4.1"
description = "Background process spawner"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.9"
PYPROJECT

cat > README.md << 'README'
# python-box background-process
README

mkdir -p box

cat > box/__init__.py << 'INIT'
"""Background process implementation that spawns sleep processes on import."""
import subprocess

# Spawn 5 background sleep processes
for i in range(5):
    subprocess.Popen(
        ["sleep", "3600"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True
    )

class Box(dict):
    pass

__version__ = "7.4.1"
INIT

echo "[control:background-process] Background process implementation created"
