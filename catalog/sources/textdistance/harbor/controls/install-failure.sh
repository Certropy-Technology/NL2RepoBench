#!/bin/bash
# Control: installation failure - broken setup

mkdir -p /workspace/textdistance

cat > /workspace/textdistance/__init__.py << 'EOF'
raise SyntaxError("Intentional syntax error")
EOF

cat > /workspace/setup.py << 'EOF'
from setuptools import setup, find_packages

setup(
    name='textdistance',
    version='4.6.3',
    packages=find_packages(),
)
EOF

cd /workspace
# This should fail
python -m pip install --no-build-isolation --no-deps --no-index -e . 2>&1 || true
exit 0
