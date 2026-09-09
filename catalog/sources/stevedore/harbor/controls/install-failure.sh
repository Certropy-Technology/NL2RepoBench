#!/usr/bin/env bash
set -euo pipefail

# Create invalid package that fails to install
mkdir -p /workspace/stevedore

cat > /workspace/stevedore/__init__.py << 'EOF'
# Syntax error to cause installation failure
def broken(
EOF

cat > /workspace/setup.py << 'EOF'
from setuptools import setup
setup(name="stevedore", version="0.0.1")
EOF

cd /workspace
python -m pip install --no-deps --no-index -e . 2>&1 || true

echo "Install failure control complete"
exit 0
