#!/bin/bash
set -euo pipefail

mkdir -p /workspace/inflect
cat > /workspace/inflect/__init__.py << 'PYEOF'
"""Intentionally broken inflect."""
syntax error this will not parse
PYEOF

cat > /workspace/setup.py << 'SETUPEOF'
from setuptools import setup, find_packages

setup(
    name="inflect",
    version="0.0.1",
    packages=find_packages(),
)
SETUPEOF

cd /workspace
python -m pip install --no-build-isolation --no-deps --no-index -e . 2>&1 || true
exit 0
