#!/usr/bin/env bash
set -euo pipefail

cd /workspace

# Create package that raises on import
mkdir -p inflection

cat > inflection/__init__.py << 'EOFPYTHON'
"""Panic control - raises immediately on import"""

raise RuntimeError("Panic control - immediate failure on import")
EOFPYTHON

cat > inflection/py.typed << 'EOFTYPED'
EOFTYPED

cat > setup.py << 'EOFSETUP'
from setuptools import setup

setup(
    name='inflection',
    version='0.5.1',
    packages=['inflection'],
    package_data={'inflection': ['py.typed']},
    zip_safe=False,
    python_requires='>=3.5',
)
EOFSETUP

cat > LICENSE << 'EOFLICENSE'
MIT License
EOFLICENSE

python -m pip install --no-build-isolation --no-deps --no-index -e .

echo "Panic control installed"
