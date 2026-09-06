#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
mkdir -p /workspace/joblib
cat > /workspace/setup.py <<'PY'
from setuptools import setup
setup(name="joblib", version="0.0.0", packages=["joblib"])
PY
printf '%s\n' 'raise RuntimeError("controlled panic")' > /workspace/joblib/__init__.py
