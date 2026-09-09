#!/usr/bin/env bash
set -euo pipefail

# Create a package with background processes
mkdir -p /workspace/stevedore

cat > /workspace/stevedore/__init__.py << 'BACKGROUND_INIT'
"""Background process - spawns daemons"""
import subprocess
import time

# Start a background sleep process
subprocess.Popen(['sleep', '3600'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

class ExtensionManager:
    def __init__(self, *args, **kwargs):
        # Spawn another background process
        subprocess.Popen(['sleep', '3600'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
BACKGROUND_INIT

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

echo "Background process control setup complete"
