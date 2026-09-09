#!/bin/bash
set -euo pipefail

# Create package with broken setup that fails to install
mkdir -p /workspace/wcwidth
cat > /workspace/setup.py << 'SETUP'
from setuptools import setup
raise RuntimeError("Intentional installation failure for control test")
SETUP

# Try to install - should fail
if pip install -e /workspace; then
    echo "ERROR: Installation should have failed but succeeded"
    exit 1
fi

echo "Install failure control: failed as expected"
exit 1
