#!/bin/bash
set -euo pipefail

# Panic control for pyperf.
# Creates a package that crashes immediately when imported.

WORKSPACE="/workspace"
cd "${WORKSPACE}"

echo "[control:panic] Creating panic package" >&2

cat > pyproject.toml << 'PYPROJECT'
[build-system]
requires = ["setuptools >= 61"]
build-backend = "setuptools.build_meta"

[project]
name = "pyperf"
version = "2.10.0"
description = "Panic pyperf package"
requires-python = ">=3.9"
dependencies = ["psutil>=5.9.0"]

[project.scripts]
pyperf = "pyperf.__main__:main"
PYPROJECT

mkdir -p pyperf

cat > pyperf/__init__.py << 'INIT'
"""Panic pyperf package."""
raise RuntimeError("Panic: immediate crash on import")
INIT

cat > pyperf/__main__.py << 'MAIN'
"""Panic CLI entry point."""
raise RuntimeError("Panic: immediate crash")
MAIN

echo "[control:panic] Panic package created" >&2
exit 0
