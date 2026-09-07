#!/bin/bash
set -euo pipefail

# Background-process control for pyperf.
# Creates a package that spawns background processes.

WORKSPACE="/workspace"
cd "${WORKSPACE}"

echo "[control:background-process] Creating background-process package" >&2

cat > pyproject.toml << 'PYPROJECT'
[build-system]
requires = ["setuptools >= 61"]
build-backend = "setuptools.build_meta"

[project]
name = "pyperf"
version = "2.10.0"
description = "Background process pyperf package"
requires-python = ">=3.9"
dependencies = ["psutil>=5.9.0"]

[project.scripts]
pyperf = "pyperf.__main__:main"
PYPROJECT

mkdir -p pyperf

cat > pyperf/__init__.py << 'INIT'
"""Background process pyperf package."""
import subprocess
import os

# Spawn background sleep processes
for i in range(5):
    subprocess.Popen(["sleep", "300"], 
                     stdout=subprocess.DEVNULL, 
                     stderr=subprocess.DEVNULL,
                     start_new_session=True)

class Run:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Background process")

class Benchmark:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Background process")

class BenchmarkSuite:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Background process")

class Runner:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Background process")

__all__ = ["Run", "Benchmark", "BenchmarkSuite", "Runner"]
INIT

cat > pyperf/__main__.py << 'MAIN'
"""Background process CLI entry point."""
import subprocess
import sys

for i in range(5):
    subprocess.Popen(["sleep", "300"], 
                     stdout=subprocess.DEVNULL, 
                     stderr=subprocess.DEVNULL,
                     start_new_session=True)

print("Background processes spawned", file=sys.stderr)
sys.exit(1)
MAIN

echo "[control:background-process] Background process package created" >&2
exit 0
