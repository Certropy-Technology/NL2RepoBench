#!/bin/bash
set -euo pipefail

# Hang control for pyperf.
# Creates a package that hangs indefinitely.

WORKSPACE="/workspace"
cd "${WORKSPACE}"

echo "[control:hang] Creating hang package" >&2

cat > pyproject.toml << 'PYPROJECT'
[build-system]
requires = ["setuptools >= 61"]
build-backend = "setuptools.build_meta"

[project]
name = "pyperf"
version = "2.10.0"
description = "Hang pyperf package"
requires-python = ">=3.9"
dependencies = ["psutil>=5.9.0"]

[project.scripts]
pyperf = "pyperf.__main__:main"
PYPROJECT

mkdir -p pyperf

cat > pyperf/__init__.py << 'INIT'
"""Hang pyperf package."""
import time

class Run:
    def __init__(self, *args, **kwargs):
        while True:
            time.sleep(1)

class Benchmark:
    def __init__(self, *args, **kwargs):
        while True:
            time.sleep(1)

class BenchmarkSuite:
    def __init__(self, *args, **kwargs):
        while True:
            time.sleep(1)

class Runner:
    def __init__(self, *args, **kwargs):
        while True:
            time.sleep(1)

__all__ = ["Run", "Benchmark", "BenchmarkSuite", "Runner"]
INIT

cat > pyperf/__main__.py << 'MAIN'
"""Hang CLI entry point."""
import time
while True:
    time.sleep(1)
MAIN

echo "[control:hang] Hang package created" >&2
exit 0
