#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/sse_starlette
printf '%s\n' 'from setuptools import setup' 'import time' 'time.sleep(600)' 'setup(name="sse-starlette", version="3.4.8", packages=["sse_starlette"])' > /workspace/setup.py
touch /workspace/sse_starlette/__init__.py
