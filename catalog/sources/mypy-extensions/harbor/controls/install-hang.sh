#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cat > /workspace/setup.py <<'EOF'
import time
time.sleep(300)
from setuptools import setup
setup(name="mypy_extensions", version="1.2.0.dev0", py_modules=["mypy_extensions"])
EOF
printf '# install-timeout control\n' > /workspace/mypy_extensions.py
