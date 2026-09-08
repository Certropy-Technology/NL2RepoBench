#!/bin/bash
set -euo pipefail

echo "[control:panic] Creating implementation that raises on import"

cd /workspace

cat > pyproject.toml << 'PYPROJECT'
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "python-box"
version = "7.4.1"
description = "Panic on import"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.9"
PYPROJECT

cat > README.md << 'README'
# python-box panic
README

mkdir -p box

cat > box/__init__.py << 'INIT'
"""Panic implementation that raises immediately on import."""
raise RuntimeError("Panic control: immediate failure on import")
INIT

echo "[control:panic] Panic implementation created"
