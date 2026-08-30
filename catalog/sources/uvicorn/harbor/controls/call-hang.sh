#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/uvicorn
printf '%s\n' 'import time' 'time.sleep(600)' > /workspace/uvicorn/__init__.py
cat > /workspace/setup.py <<'PY'
from setuptools import setup

setup(name="uvicorn", version="0.52.4", packages=["uvicorn"])
PY
