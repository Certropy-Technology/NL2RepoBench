#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
mkdir -p /workspace/smmap
printf '__version__ = "0.0.0"\n' > /workspace/smmap/__init__.py
cat > /workspace/setup.py <<'PY'
from setuptools import setup

setup(name="smmap", version="0.0.0", packages=["smmap"])
PY
