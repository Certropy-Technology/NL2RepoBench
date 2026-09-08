#!/usr/bin/env bash
set -euo pipefail

# Stub control: minimal package with NotImplementedError stubs

cd /workspace

# Create package structure
mkdir -p tabulate

# Create stub __init__.py
cat > tabulate/__init__.py << 'ENDPY'
"""Stub implementation of tabulate"""

__version__ = "0.0.0-stub"

def tabulate(*args, **kwargs):
    raise NotImplementedError("tabulate is not implemented")

def simple_separated_format(*args, **kwargs):
    raise NotImplementedError("simple_separated_format is not implemented")

tabulate_formats = []

def _main():
    raise NotImplementedError("CLI not implemented")

__all__ = ["tabulate", "tabulate_formats", "simple_separated_format"]
ENDPY

# Create pyproject.toml
cat > pyproject.toml << 'ENDTOML'
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[project]
name = "tabulate"
version = "0.0.0"
description = "Stub"
requires-python = ">=3.10"

[project.scripts]
tabulate = "tabulate:_main"
ENDTOML

# Install
python -m pip install --no-build-isolation --no-deps --no-index -e .

echo "Stub control installed"
