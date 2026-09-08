#!/bin/bash
set -euo pipefail

# Create working implementation but spawn background process
mkdir -p /workspace
cat > /workspace/toposort.py << 'BGCODE'
import subprocess
import sys

__version__ = "1.10"
__all__ = ["toposort", "toposort_flatten", "CircularDependencyError"]

# Spawn a background process that sleeps
try:
    subprocess.Popen([sys.executable, "-c", "import time; time.sleep(300)"], 
                     stdout=subprocess.DEVNULL, 
                     stderr=subprocess.DEVNULL,
                     start_new_session=True)
except:
    pass

class CircularDependencyError(ValueError):
    def __init__(self, data):
        s = f"Circular dependencies exist among these items: {{{', '.join(f'{key}:{value}' for key, value in data.items())}}}"
        super().__init__(s)
        self.data = data

def toposort(data):
    if len(data) == 0:
        return
    data = {item: set(e for e in dep if e != item) for item, dep in data.items()}
    extra_items_in_deps = {value for values in data.values() for value in values} - set(data.keys())
    data.update({item: set() for item in extra_items_in_deps})
    while True:
        ordered = set(item for item, dep in data.items() if len(dep) == 0)
        if not ordered:
            break
        yield ordered
        data = {item: (dep - ordered) for item, dep in data.items() if item not in ordered}
    if len(data) != 0:
        raise CircularDependencyError(data)

def toposort_flatten(data, sort=True):
    result = []
    for d in toposort(data):
        result.extend((sorted if sort else list)(d))
    return result
BGCODE

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
python -c "import toposort; print('Background process control installed')"
