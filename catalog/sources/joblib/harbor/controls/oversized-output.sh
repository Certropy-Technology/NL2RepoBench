#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
mkdir -p /workspace/joblib
cat > /workspace/setup.py <<'PY'
from setuptools import setup
setup(name="joblib", version="0.0.0", packages=["joblib"])
PY
cat > /workspace/joblib/__init__.py <<'PY'
def oversized(*args, **kwargs):
    return "x" * (16 * 1024 * 1024)
__all__ = ["oversized"]
PY
