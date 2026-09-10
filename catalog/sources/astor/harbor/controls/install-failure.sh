#!/bin/bash
set -euo pipefail

echo "[control:install-failure] Creating package with broken installation"

cd /workspace

# Create invalid setup.py
cat > setup.py << 'SETUP'
from setuptools import setup

# Invalid syntax - missing closing parenthesis
setup(
    name='astor',
    version='0.8.1',
    # Missing required fields and invalid syntax
    this is not valid python !!!
SETUP

echo "[control:install-failure] Created invalid setup.py"
