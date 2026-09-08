#!/bin/bash
set -euo pipefail

# Create implementation that produces excessive output
mkdir -p /workspace
cat > /workspace/toposort.py << 'OVERSIZEDCODE'
__version__ = "1.10"
__all__ = ["toposort", "toposort_flatten", "CircularDependencyError"]

class CircularDependencyError(ValueError):
    def __init__(self, data):
        super().__init__("Circular dependencies exist")
        self.data = data

def toposort(data):
    # Print massive output
    for i in range(100000):
        print(f"Oversized output line {i}: " + "X" * 1000)
    if not data:
        return
    yield set(data.keys())

def toposort_flatten(data, sort=True):
    for i in range(100000):
        print(f"Flatten oversized {i}: " + "Y" * 1000)
    return list(data.keys())
OVERSIZEDCODE

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
python -c "import toposort; print('Oversized control installed')"
