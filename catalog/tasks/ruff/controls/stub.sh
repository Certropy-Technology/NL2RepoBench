#!/usr/bin/env bash
set -euo pipefail

cat > /workspace/setup.py <<'PY'
from setuptools import setup

setup(name="ruff", version="0.16.4", packages=["ruff"])
PY
mkdir -p /workspace/ruff
cat > /workspace/ruff/__init__.py <<'PY'
__version__ = "0.16.4"
PY
