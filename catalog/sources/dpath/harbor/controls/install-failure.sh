#!/bin/bash
set -euo pipefail

echo "[control:install-failure] Creating package that fails to install"

cd /workspace

# Create a setup.py that will fail
cat > setup.py << 'SETUP'
from setuptools import setup
import sys

# Force installation failure
sys.exit(1)
SETUP

echo "[control:install-failure] Created package with failing setup.py"
