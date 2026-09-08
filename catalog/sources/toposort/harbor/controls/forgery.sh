#!/bin/bash
set -euo pipefail

# Create forgery that tries to fake results
mkdir -p /workspace
cat > /workspace/toposort.py << 'FORGERYCODE'
__version__ = "1.10"
__all__ = ["toposort", "toposort_flatten", "CircularDependencyError"]

class CircularDependencyError(ValueError):
    def __init__(self, data):
        super().__init__("Circular dependencies exist")
        self.data = data

def toposort(data):
    # Forgery: returns wrong structure
    if not data:
        return
    yield set(data.keys())

def toposort_flatten(data, sort=True):
    # Forgery: returns wrong order
    result = []
    for s in toposort(data):
        result.extend(list(s))
    return result
FORGERYCODE

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
python -c "import toposort; print('Forgery installed')"
