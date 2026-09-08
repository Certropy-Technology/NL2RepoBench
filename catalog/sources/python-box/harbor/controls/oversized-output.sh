#!/bin/bash
set -euo pipefail

echo "[control:oversized-output] Creating implementation that floods stderr on import"

cd /workspace

cat > pyproject.toml << 'PYPROJECT'
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "python-box"
version = "7.4.1"
description = "Oversized output"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.9"
PYPROJECT

cat > README.md << 'README'
# python-box oversized
README

mkdir -p box

cat > box/__init__.py << 'INIT'
"""Oversized output implementation that floods stderr on import."""
import sys

# Flood stderr with 100K lines
for i in range(100000):
    print(f"OVERSIZED_OUTPUT_LINE_{i:06d}_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX", file=sys.stderr)

class Box(dict):
    pass

__version__ = "7.4.1"
INIT

echo "[control:oversized-output] Oversized output implementation created"
