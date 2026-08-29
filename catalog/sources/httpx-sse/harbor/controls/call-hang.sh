#!/usr/bin/env bash
set -euo pipefail

cat > /workspace/setup.py <<'PY'
from setuptools import setup

setup(name="httpx-sse", version="0.4.3", packages=["httpx_sse"])
PY

mkdir -p /workspace/httpx_sse
printf '%s\n' 'import time; time.sleep(600)' > /workspace/httpx_sse/__init__.py
