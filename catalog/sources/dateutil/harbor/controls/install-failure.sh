#!/bin/bash
set -euo pipefail

cd /workspace

mkdir -p src/dateutil

# Invalid pyproject.toml to cause installation failure
cat > pyproject.toml << 'INVALID_EOF'
[build-system
requires = ["setuptools"
build-backend = "setuptools.build_meta"
INVALID_EOF

cat > setup.cfg << 'SETUP_EOF'
[metadata]
name = python-dateutil
version = 2.9.0.post0
SETUP_EOF

cat > setup.py << 'SETUP_PY_EOF'
from setuptools import setup
setup()
SETUP_PY_EOF

# Try to install (should fail)
python -m pip install --no-build-isolation --no-deps --no-index -e . || exit 0
