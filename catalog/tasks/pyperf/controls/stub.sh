#!/bin/bash
set -euo pipefail

# Stub control for pyperf.
# Creates minimal packaging structure that can be installed but fails tests.

WORKSPACE="/workspace"
cd "${WORKSPACE}"

echo "[control:stub] Creating stub pyperf package" >&2

# Create pyproject.toml
cat > pyproject.toml << 'PYPROJECT'
[build-system]
requires = ["setuptools >= 61"]
build-backend = "setuptools.build_meta"

[project]
name = "pyperf"
version = "2.10.0"
description = "Stub pyperf package"
requires-python = ">=3.9"
dependencies = ["psutil>=5.9.0"]

[project.scripts]
pyperf = "pyperf.__main__:main"
PYPROJECT

# Create pyperf package directory
mkdir -p pyperf

# Create __init__.py with stub exports that raise NotImplementedError
cat > pyperf/__init__.py << 'INIT'
"""Stub pyperf package."""
__version__ = "2.10.0"

class Run:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Stub implementation")

class Benchmark:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Stub implementation")

class BenchmarkSuite:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Stub implementation")
    
    @classmethod
    def load(cls, *args, **kwargs):
        raise NotImplementedError("Stub implementation")
    
    @classmethod
    def loads(cls, *args, **kwargs):
        raise NotImplementedError("Stub implementation")

class Runner:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Stub implementation")

def add_runs(*args, **kwargs):
    raise NotImplementedError("Stub implementation")

def format_metadata(*args, **kwargs):
    raise NotImplementedError("Stub implementation")

def python_implementation():
    raise NotImplementedError("Stub implementation")

def python_has_jit():
    raise NotImplementedError("Stub implementation")

perf_counter = None

__all__ = [
    "Run", "Benchmark", "BenchmarkSuite", "Runner", 
    "add_runs", "format_metadata", 
    "python_implementation", "python_has_jit", "perf_counter"
]
INIT

# Create __main__.py stub
cat > pyperf/__main__.py << 'MAIN'
"""Stub CLI entry point."""
import sys

def main():
    print("pyperf stub: not implemented", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    main()
MAIN

echo "[control:stub] Stub package created" >&2
exit 0
