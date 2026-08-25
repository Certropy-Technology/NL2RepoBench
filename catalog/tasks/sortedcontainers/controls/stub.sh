#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/sortedcontainers
cat > /workspace/setup.py <<'PY'
from setuptools import setup

setup(name="sortedcontainers", version="2.4.0", packages=["sortedcontainers"])
PY
cat > /workspace/sortedcontainers/__init__.py <<'PY'
__version__ = "2.4.0"
PY
