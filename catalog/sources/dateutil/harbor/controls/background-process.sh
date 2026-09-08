#!/bin/bash
set -euo pipefail

cd /workspace

mkdir -p src/dateutil

cat > pyproject.toml << 'PYPROJECT_EOF'
[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"
PYPROJECT_EOF

cat > setup.cfg << 'SETUP_EOF'
[metadata]
name = python-dateutil
version = 2.9.0.post0

[options]
package_dir =
    =src
packages = find:

[options.packages.find]
where = src
SETUP_EOF

cat > setup.py << 'SETUP_PY_EOF'
from setuptools import setup
setup()
SETUP_PY_EOF

# Spawn background processes on import
cat > src/dateutil/__init__.py << 'BACKGROUND_EOF'
import subprocess
import time

# Spawn 5 background processes that sleep
for i in range(5):
    subprocess.Popen(['sleep', '3600'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
BACKGROUND_EOF

# Install
python -m pip install --no-build-isolation --no-deps --no-index -e .
