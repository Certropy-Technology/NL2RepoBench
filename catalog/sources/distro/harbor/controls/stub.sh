#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/distro
cat > /workspace/setup.py <<'PY'
from setuptools import setup
setup(name="distro", version="1.9.0", packages=["distro"])
PY
cat > /workspace/distro/__init__.py <<'PY'
__version__ = "1.9.0"
PY
