#!/bin/bash
set -euo pipefail

# Create a malformed package that will fail to install
mkdir -p /workspace/pycountry

cat > /workspace/setup.py << 'PYEOF'
from setuptools import setup

# This will fail during installation
raise RuntimeError("Intentional installation failure for testing")
PYEOF

cd /workspace
python -m pip install --no-deps --no-index -e . || true
