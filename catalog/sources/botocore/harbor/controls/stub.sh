#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
mkdir -p /workspace/botocore
cat > /workspace/setup.py <<'PY'
from setuptools import setup
setup(name="botocore", version="0.0.0", packages=["botocore"])
PY
cat > /workspace/botocore/__init__.py <<'PY'
__version__ = "0.0.0"
PY
