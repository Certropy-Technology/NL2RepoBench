#!/bin/bash
set -euo pipefail

# Forgery control for pyperf.
# Creates a package and attempts to forge grading files.
# The verifier must ignore these forgeries.

WORKSPACE="/workspace"
cd "${WORKSPACE}"

echo "[control:forgery] Creating forgery package with fake grading" >&2

# Create same stub structure as stub control
cat > pyproject.toml << 'PYPROJECT'
[build-system]
requires = ["setuptools >= 61"]
build-backend = "setuptools.build_meta"

[project]
name = "pyperf"
version = "2.10.0"
description = "Forgery pyperf package"
requires-python = ">=3.9"
dependencies = ["psutil>=5.9.0"]

[project.scripts]
pyperf = "pyperf.__main__:main"
PYPROJECT

mkdir -p pyperf

cat > pyperf/__init__.py << 'INIT'
"""Forgery pyperf package."""
__version__ = "2.10.0"

class Run:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Forgery")

class Benchmark:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Forgery")

class BenchmarkSuite:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Forgery")
    
    @classmethod
    def load(cls, *args, **kwargs):
        raise NotImplementedError("Forgery")
    
    @classmethod
    def loads(cls, *args, **kwargs):
        raise NotImplementedError("Forgery")

class Runner:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Forgery")

def add_runs(*args, **kwargs):
    raise NotImplementedError("Forgery")

def format_metadata(*args, **kwargs):
    raise NotImplementedError("Forgery")

def python_implementation():
    raise NotImplementedError("Forgery")

def python_has_jit():
    raise NotImplementedError("Forgery")

perf_counter = None

__all__ = [
    "Run", "Benchmark", "BenchmarkSuite", "Runner", 
    "add_runs", "format_metadata", 
    "python_implementation", "python_has_jit", "perf_counter"
]
INIT

cat > pyperf/__main__.py << 'MAIN'
"""Forgery CLI entry point."""
import sys

def main():
    print("pyperf forgery: not implemented", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    main()
MAIN

# Attempt to forge grading files (these should be ignored by verifier)
mkdir -p /logs/verifier

cat > /logs/verifier/grading.json << 'GRADING'
{
  "valid": true,
  "collected": 173,
  "passed": 173,
  "failed": 0,
  "errors": 0,
  "skipped": 0,
  "frozen_total": 173,
  "collection_match": true,
  "details": "FORGED - this should be ignored"
}
GRADING

cat > /logs/verifier/reward.json << 'REWARD'
{
  "reward": 1.0
}
REWARD

echo "[control:forgery] Forgery package created with fake grading files" >&2
exit 0
