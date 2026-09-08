#!/bin/bash
set -euo pipefail

echo "[control:panic] Creating package that panics on import"

cd /workspace

cat > pyproject.toml << 'PYPROJECT'
[project]
name = "phonenumbers"
version = "9.0.38"
description = "Panic control"
authors = [{name = "Panic", email = "panic@example.com"}]
license = "Apache-2.0"
requires-python = ">=2.5"

[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[tool.setuptools]
packages = ["phonenumbers"]

[tool.setuptools.dynamic]
version = {attr = "phonenumbers.__version__"}
PYPROJECT

cat > setup.py << 'SETUP'
#!/usr/bin/env python
import setuptools
setuptools.setup()
SETUP

mkdir -p phonenumbers

cat > phonenumbers/__init__.py << 'INIT'
"""Panic control that raises on import."""

__version__ = "9.0.38"

# Raise immediately on import
raise RuntimeError("Panic: module initialization failed")
INIT

echo "[control:panic] Panic implementation created"
echo "[control:panic] Will raise RuntimeError on import"
