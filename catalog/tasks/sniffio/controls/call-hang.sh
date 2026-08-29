#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/sniffio
cat > /workspace/setup.py <<'PY'
from setuptools import setup

setup(name="sniffio", version="1.3.1+dev", packages=["sniffio"])
PY
cat > /workspace/sniffio/__init__.py <<'PY'
while True:
    pass
PY
