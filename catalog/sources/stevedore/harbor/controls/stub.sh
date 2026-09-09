#!/usr/bin/env bash
set -euo pipefail

# Create minimal package structure with stub implementations
mkdir -p /workspace/stevedore

cat > /workspace/stevedore/__init__.py << 'STUB_INIT'
"""Stub stevedore package - all managers raise NotImplementedError"""

__all__ = [
    'ExtensionManager',
    'EnabledExtensionManager',
    'NamedExtensionManager',
    'HookManager',
    'DriverManager',
]

class ExtensionManager:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("ExtensionManager not implemented")

class EnabledExtensionManager:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("EnabledExtensionManager not implemented")

class NamedExtensionManager:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("NamedExtensionManager not implemented")

class HookManager:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("HookManager not implemented")

class DriverManager:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("DriverManager not implemented")
STUB_INIT

mkdir -p /workspace/stevedore/exception

cat > /workspace/stevedore/exception.py << 'STUB_EXCEPTION'
"""Stub exception classes"""

class NoUniqueMatch(RuntimeError):
    pass

class NoMatches(NoUniqueMatch):
    pass

class MultipleMatches(NoUniqueMatch):
    pass
STUB_EXCEPTION

cat > /workspace/pyproject.toml << 'STUB_PYPROJECT'
[build-system]
requires = []
build-backend = "flit_core.buildapi"

[project]
name = "stevedore"
version = "0.0.1"
description = "Stub implementation"
STUB_PYPROJECT

cat > /workspace/setup.py << 'STUB_SETUP'
from setuptools import setup, find_packages
setup(name="stevedore", version="0.0.1", packages=find_packages())
STUB_SETUP

# Install the stub
cd /workspace
python -m pip install --no-deps --no-index -e .

echo "Stub setup complete"
