#!/bin/bash
set -euo pipefail

echo "[control:install-failure] Creating package that will fail to install"

cd /workspace

# Create a broken setup.py
cat > setup.py << 'SETUP'
from setuptools import setup

# This will cause installation to fail
raise RuntimeError("Installation deliberately fails")

setup(
    name="records",
    version="0.6.0",
)
SETUP

echo "[control:install-failure] Broken package created"
