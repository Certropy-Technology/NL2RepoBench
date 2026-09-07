#!/bin/bash
set -euo pipefail

# Oversized-output control for pyperf.
# Creates a package that produces excessive output.

WORKSPACE="/workspace"
cd "${WORKSPACE}"

echo "[control:oversized-output] Creating oversized-output package" >&2

cat > pyproject.toml << 'PYPROJECT'
[build-system]
requires = ["setuptools >= 61"]
build-backend = "setuptools.build_meta"

[project]
name = "pyperf"
version = "2.10.0"
description = "Oversized output pyperf package"
requires-python = ">=3.9"
dependencies = ["psutil>=5.9.0"]

[project.scripts]
pyperf = "pyperf.__main__:main"
PYPROJECT

mkdir -p pyperf

cat > pyperf/__init__.py << 'INIT'
"""Oversized output pyperf package."""

class Run:
    def __init__(self, *args, **kwargs):
        # Print 10MB of output
        for i in range(100000):
            print("X" * 100)
        raise NotImplementedError("Oversized output")

class Benchmark:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Oversized output")

class BenchmarkSuite:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Oversized output")

class Runner:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Oversized output")

__all__ = ["Run", "Benchmark", "BenchmarkSuite", "Runner"]
INIT

cat > pyperf/__main__.py << 'MAIN'
"""Oversized output CLI entry point."""
import sys
for i in range(100000):
    print("X" * 100)
sys.exit(1)
MAIN

echo "[control:oversized-output] Oversized output package created" >&2
exit 0
