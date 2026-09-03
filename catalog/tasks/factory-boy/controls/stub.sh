#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/factory
cat > /workspace/factory/__init__.py <<'PY'
class Factory:
    pass
PY
cat > /workspace/setup.py <<'PY'
from setuptools import setup
setup(name="factory_boy", version="3.3.4.dev0", packages=["factory"])
PY
