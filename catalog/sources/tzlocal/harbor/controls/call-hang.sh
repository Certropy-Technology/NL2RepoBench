#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/tzlocal
cat > /workspace/setup.py <<'PY'
from setuptools import setup

setup(name="tzlocal", version="5.4.5.dev0", packages=["tzlocal"])
PY
cat > /workspace/tzlocal/__init__.py <<'PY'
while True:
    pass
PY
