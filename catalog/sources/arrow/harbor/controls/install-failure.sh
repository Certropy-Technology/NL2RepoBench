#!/bin/bash
set -euo pipefail

# Create a package that fails during installation
mkdir -p /workspace/arrow
cat > /workspace/arrow/__init__.py << 'INIT'
__version__ = "1.4.0"
INIT

cat > /workspace/setup.py << 'SETUP_PY'
from setuptools import setup
import sys

# Force installation failure
sys.exit(1)

setup(
    name="arrow",
    version="1.4.0",
)
SETUP_PY

cd /workspace
python -m pip install --no-deps --no-index -e . || true
