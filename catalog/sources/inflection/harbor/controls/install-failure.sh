#!/usr/bin/env bash
set -euo pipefail

cd /workspace

# Create invalid package that will fail to install
mkdir -p inflection

cat > inflection/__init__.py << 'EOFPYTHON'
"""This would be valid code"""
__version__ = '0.5.1'
EOFPYTHON

cat > setup.py << 'EOFSETUP'
from setuptools import setup

setup(
    name='inflection',
    version='0.5.1',
    packages=['inflection'],
EOFSETUP
# Intentionally invalid - missing closing parenthesis

cat > LICENSE << 'EOFLICENSE'
MIT License
EOFLICENSE

echo "Install-failure control created with invalid setup.py"
