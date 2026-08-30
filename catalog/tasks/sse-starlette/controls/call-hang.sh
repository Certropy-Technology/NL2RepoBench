#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/sse_starlette
printf '%s\n' 'import time; time.sleep(600)' > /workspace/sse_starlette/__init__.py
printf '%s\n' 'import time; time.sleep(600)' > /workspace/sse_starlette/event.py
printf '%s\n' 'import time; time.sleep(600)' > /workspace/sse_starlette/sse.py
cat > /workspace/setup.py <<'PY'
from setuptools import setup

setup(name="sse-starlette", version="3.4.8", packages=["sse_starlette"])
PY
