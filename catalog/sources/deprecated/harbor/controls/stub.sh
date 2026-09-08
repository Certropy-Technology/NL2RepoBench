#!/bin/bash
set -euo pipefail

echo "[control:stub] Creating stub implementation with correct package structure but non-functional code"

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

# Create __init__.py with stub exports that raise NotImplementedError
cat > deprecated/__init__.py << 'INIT'
"""Stub implementation of deprecated."""

__version__ = "1.3.1"

def deprecated(*args, **kwargs):
    raise NotImplementedError("Stub implementation")

class DeprecatedParams:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Stub implementation")
    def __call__(self, *args, **kwargs):
        raise NotImplementedError("Stub implementation")

deprecated_params = DeprecatedParams
INIT

# Create classic.py
cat > deprecated/classic.py << 'CLASSIC'
"""Stub classic module."""

def deprecated(*args, **kwargs):
    raise NotImplementedError("Stub implementation")

class ClassicAdapter:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Stub implementation")
    def __call__(self, *args, **kwargs):
        raise NotImplementedError("Stub implementation")
CLASSIC

# Create sphinx.py
cat > deprecated/sphinx.py << 'SPHINX'
"""Stub sphinx module."""

def deprecated(*args, **kwargs):
    raise NotImplementedError("Stub implementation")

def versionadded(*args, **kwargs):
    raise NotImplementedError("Stub implementation")

def versionchanged(*args, **kwargs):
    raise NotImplementedError("Stub implementation")

class SphinxAdapter:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Stub implementation")
    def __call__(self, *args, **kwargs):
        raise NotImplementedError("Stub implementation")
SPHINX

# Create params.py
cat > deprecated/params.py << 'PARAMS'
"""Stub params module."""

class DeprecatedParams:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Stub implementation")
    def __call__(self, *args, **kwargs):
        raise NotImplementedError("Stub implementation")

deprecated_params = DeprecatedParams
PARAMS

echo "[control:stub] Stub implementation created"
echo "[control:stub] Package structure is correct but all functions raise NotImplementedError"
