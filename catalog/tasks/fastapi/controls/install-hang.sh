#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cat > /workspace/setup.py <<'EOF'
import time
from setuptools import setup
time.sleep(600)
setup(name="fastapi", version="0.141.1")
EOF
