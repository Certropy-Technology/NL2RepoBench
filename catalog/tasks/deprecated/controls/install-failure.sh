#!/bin/bash
set -euo pipefail

echo "[control:install-failure] Creating malformed package that fails installation"

cd /workspace

# Create invalid setup.py that will fail
cat > setup.py << 'SETUP'
from setuptools import setup

# This will fail during installation
raise RuntimeError("Intentional installation failure for testing")

setup(name="Deprecated")
SETUP

echo "[control:install-failure] Created package that will fail to install"
exit 0
