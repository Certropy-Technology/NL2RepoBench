#!/bin/bash
set -euo pipefail

echo "[control:install-failure] Creating broken setup that will fail installation"

cd /workspace

# Create invalid setup.py with syntax error
cat > setup.py << 'SETUP'
from setuptools import setup, find_packages

setup(
    name="natsort",
    version="8.4.0"
    # Missing comma - syntax error
    description="This will fail to install",
)
SETUP

echo "[control:install-failure] Created broken setup.py"
echo "[control:install-failure] Installation will fail due to syntax error"
