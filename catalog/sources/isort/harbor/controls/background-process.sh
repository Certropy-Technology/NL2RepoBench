#!/bin/bash
set -euo pipefail

echo "=== Background Process Control: Package that spawns background processes ==="

mkdir -p /workspace/isort

cat > /workspace/pyproject.toml << 'EOFPYPROJECT'
[project]
name = "isort"
version = "9.0.1"
requires-python = ">=3.10.0"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
EOFPYPROJECT

# Create package that spawns background processes on import
cat > /workspace/isort/__init__.py << 'EOFINIT'
import subprocess
import sys

# Spawn 5 background processes that sleep
for i in range(5):
    subprocess.Popen([sys.executable, "-c", "import time; time.sleep(300)"], 
                     stdout=subprocess.DEVNULL, 
                     stderr=subprocess.DEVNULL)

__version__ = "9.0.1"
EOFINIT

cd /workspace
python -m pip install --no-build-isolation --no-deps --no-index -e .

echo "=== Background process control installed ==="
