#!/bin/bash
set -euo pipefail

echo "[control:oversized-output] Creating implementation that generates excessive output"

cd /workspace

# Create setup.py
cat > setup.py << 'SETUP'
from setuptools import setup

setup(
    name="Deprecated",
    version="1.3.1",
    packages=["deprecated"],
    install_requires=["wrapt>=1.10,<3"],
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
)
SETUP

# Create deprecated package
mkdir -p deprecated

# Create __init__.py that generates massive output
cat > deprecated/__init__.py << 'INIT'
"""Oversized output implementation."""
import sys

__version__ = "1.3.1"

# Generate lots of output on import
for i in range(100000):
    print(f"Line {i}: " + "x" * 100)
    sys.stdout.flush()

def deprecated(*args, **kwargs):
    if len(args) == 1 and callable(args[0]):
        return args[0]
    def decorator(func):
        return func
    return decorator

class DeprecatedParams:
    def __init__(self, *args, **kwargs):
        pass
    def __call__(self, func):
        return func

deprecated_params = DeprecatedParams
INIT

cat > deprecated/classic.py << 'CLASSIC'
def deprecated(*args, **kwargs):
    if len(args) == 1 and callable(args[0]):
        return args[0]
    def decorator(func):
        return func
    return decorator

class ClassicAdapter:
    def __init__(self, *args, **kwargs):
        pass
    def __call__(self, func):
        return func
CLASSIC

cat > deprecated/sphinx.py << 'SPHINX'
def deprecated(*args, **kwargs):
    if len(args) == 1 and callable(args[0]):
        return args[0]
    def decorator(func):
        return func
    return decorator

def versionadded(*args, **kwargs):
    def decorator(func):
        return func
    return decorator

def versionchanged(*args, **kwargs):
    def decorator(func):
        return func
    return decorator

class SphinxAdapter:
    def __init__(self, *args, **kwargs):
        pass
    def __call__(self, func):
        return func
SPHINX

cat > deprecated/params.py << 'PARAMS'
class DeprecatedParams:
    def __init__(self, *args, **kwargs):
        pass
    def __call__(self, func):
        return func

deprecated_params = DeprecatedParams
PARAMS

echo "[control:oversized-output] Oversized output implementation created"
