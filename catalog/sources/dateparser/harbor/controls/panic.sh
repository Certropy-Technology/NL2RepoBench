#!/bin/bash
set -euo pipefail

echo "[control:panic] Creating package that raises on import"

cd /workspace

# Create pyproject.toml
cat > pyproject.toml << 'PYPROJECT'
[build-system]
build-backend = "setuptools.build_meta"
requires = ["setuptools >= 77.0"]

[project]
name = "dateparser"
version = "1.4.3"
description = "Date parsing library designed to parse dates from HTML pages"
authors = [{ name = "Panic", email = "panic@example.com" }]
license = "BSD-3-Clause"
requires-python = ">=3.10"
dependencies = [
    "python-dateutil>=2.7.0",
    "pytz>=2024.2",
    "regex>=2024.9.11",
    "tzlocal>=0.2",
]
PYPROJECT

# Create package directory
mkdir -p dateparser

# Create __init__.py that raises on import
cat > dateparser/__init__.py << 'INIT'
"""Panic implementation that crashes on import."""

__version__ = "1.4.3"

raise RuntimeError("Panic control: package crashes on import")
INIT

echo "[control:panic] Package that raises on import created"
