#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/alembic
cat > /workspace/setup.py <<'PY'
from setuptools import setup
setup(name="alembic", version="1.19.2", packages=["alembic"])
PY
cat > /workspace/alembic/__init__.py <<'PY'
while True:
    pass
PY
