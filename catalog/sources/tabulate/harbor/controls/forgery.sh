#!/usr/bin/env bash
set -euo pipefail

# Forgery control: looks correct but returns wrong values

cd /workspace

mkdir -p tabulate

cat > tabulate/__init__.py << 'ENDPY'
"""Forgery implementation"""

__version__ = "0.0.0-forgery"

def tabulate(data, headers=(), tablefmt="simple", **kwargs):
    """Always return a fixed wrong output"""
    return "FORGERY_OUTPUT"

def simple_separated_format(separator):
    """Return a fake format object"""
    return "fake_format"

tabulate_formats = ["fake1", "fake2", "fake3"]

def _main():
    print("Forgery CLI")

__all__ = ["tabulate", "tabulate_formats", "simple_separated_format"]
ENDPY

cat > pyproject.toml << 'ENDTOML'
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[project]
name = "tabulate"
version = "0.0.0"
description = "Forgery"
requires-python = ">=3.10"

[project.scripts]
tabulate = "tabulate:_main"
ENDTOML

python -m pip install --no-build-isolation --no-deps --no-index -e .

echo "Forgery control installed"
