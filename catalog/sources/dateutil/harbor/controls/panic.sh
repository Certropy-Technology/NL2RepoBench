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

# Panic on import
cat > src/dateutil/__init__.py << 'PANIC_EOF'
raise RuntimeError("Panic control: import raises exception immediately")
PANIC_EOF

# Install
python -m pip install --no-build-isolation --no-deps --no-index -e .
