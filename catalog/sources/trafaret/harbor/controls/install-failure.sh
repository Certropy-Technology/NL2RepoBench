#!/bin/bash
set -euo pipefail

echo "[control:install-failure] Creating package with broken installation"

cd /workspace

# Create invalid setup.py with syntax error
cat > setup.py << 'SETUP'
#!/usr/bin/env python
from setuptools import setup

# This is intentionally broken - missing closing parenthesis
setup(
    name='trafaret',
    version='2.1.1'
    # Missing comma and closing parenthesis - syntax error
SETUP

echo "[control:install-failure] Created invalid setup.py with syntax error"
