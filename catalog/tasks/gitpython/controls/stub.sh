#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
cat > /workspace/setup.py <<'PY'
from setuptools import setup

setup(name="GitPython", version="3.1.60", packages=["git"])
PY
mkdir -p /workspace/git
printf '%s\n' '__version__ = "3.1.60"' > /workspace/git/__init__.py
