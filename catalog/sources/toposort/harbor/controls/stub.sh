#!/bin/bash
set -euo pipefail

# Create stub implementation with NotImplementedError
mkdir -p /workspace
cat > /workspace/toposort.py << 'STUBCODE'
__version__ = "1.10"
__all__ = ["toposort", "toposort_flatten", "CircularDependencyError"]

class CircularDependencyError(ValueError):
    def __init__(self, data):
        super().__init__("Circular dependencies exist")
        self.data = data

def toposort(data):
    raise NotImplementedError("toposort not implemented")

def toposort_flatten(data, sort=True):
    raise NotImplementedError("toposort_flatten not implemented")
STUBCODE

# Install stub as editable package
cd /workspace
cat > setup.py << 'SETUP'
from setuptools import setup
setup(
    name="toposort",
    version="1.10",
    py_modules=["toposort"],
)
SETUP

python -m pip install --no-deps -e .
python -c "import toposort; print('Stub installed')"
