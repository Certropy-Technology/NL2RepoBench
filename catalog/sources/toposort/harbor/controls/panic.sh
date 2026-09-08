#!/bin/bash
set -euo pipefail

# Create implementation that crashes/panics
mkdir -p /workspace
cat > /workspace/toposort.py << 'PANICCODE'
__version__ = "1.10"
__all__ = ["toposort", "toposort_flatten", "CircularDependencyError"]

class CircularDependencyError(ValueError):
    def __init__(self, data):
        super().__init__("Circular dependencies exist")
        self.data = data

def toposort(data):
    raise RuntimeError("Panic: toposort crashed")

def toposort_flatten(data, sort=True):
    raise RuntimeError("Panic: toposort_flatten crashed")
PANICCODE

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
python -c "import toposort; print('Panic control installed')"
