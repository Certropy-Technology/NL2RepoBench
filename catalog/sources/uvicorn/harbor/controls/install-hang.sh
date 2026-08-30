#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/uvicorn
printf '%s\n' 'from setuptools import setup' 'import time' 'time.sleep(600)' 'setup(name="uvicorn", version="0.52.4", packages=["uvicorn"])' > /workspace/setup.py
touch /workspace/uvicorn/__init__.py
