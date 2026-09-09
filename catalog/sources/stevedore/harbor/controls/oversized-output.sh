#!/usr/bin/env bash
set -euo pipefail

# Create a package that produces oversized output
mkdir -p /workspace/stevedore

cat > /workspace/stevedore/__init__.py << 'OVERSIZED_INIT'
"""Oversized output - prints huge amounts of data"""
import sys

# Print 50MB of data to stderr immediately
for i in range(50000):
    print("X" * 1000, file=sys.stderr)

class ExtensionManager:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError()

class DriverManager:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError()

class NamedExtensionManager:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError()

class EnabledExtensionManager:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError()

class HookManager:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError()

__all__ = ['ExtensionManager', 'DriverManager', 'NamedExtensionManager', 'EnabledExtensionManager', 'HookManager']
OVERSIZED_INIT

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

echo "Oversized output control setup complete"
