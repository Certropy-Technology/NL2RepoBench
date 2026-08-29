#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/python_discovery
cat > /workspace/setup.py <<'PY'
from setuptools import setup

setup(name="python-discovery", version="0.0.0", packages=["python_discovery"])
PY
cat > /workspace/python_discovery/__init__.py <<'PY'
while True:
    pass
PY
