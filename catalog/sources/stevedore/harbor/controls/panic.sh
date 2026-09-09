#!/usr/bin/env bash
set -euo pipefail

# Create a package that imports successfully but panics on use
mkdir -p /workspace/stevedore

cat > /workspace/stevedore/__init__.py << 'PANIC_INIT'
"""Panic implementation - crashes on manager creation"""
import sys

class ExtensionManager:
    def __init__(self, *args, **kwargs):
        sys.exit(42)

class DriverManager:
    def __init__(self, *args, **kwargs):
        sys.exit(42)

class NamedExtensionManager:
    def __init__(self, *args, **kwargs):
        sys.exit(42)

class EnabledExtensionManager:
    def __init__(self, *args, **kwargs):
        sys.exit(42)

class HookManager:
    def __init__(self, *args, **kwargs):
        sys.exit(42)

__all__ = ['ExtensionManager', 'DriverManager', 'NamedExtensionManager', 'EnabledExtensionManager', 'HookManager']
PANIC_INIT

cat > /workspace/stevedore/exception.py << 'EOF'
class NoUniqueMatch(RuntimeError):
    pass
class NoMatches(NoUniqueMatch):
    pass
class MultipleMatches(NoUniqueMatch):
    pass
EOF

cat > /workspace/setup.py << 'EOF'
from setuptools import setup, find_packages
setup(name="stevedore", version="0.0.1", packages=find_packages())
EOF

cd /workspace
python -m pip install --no-deps --no-index -e .

echo "Panic control setup complete"
