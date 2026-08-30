#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/uvicorn
printf '%s\n' '__version__ = "0.52.4"' '__all__ = ["main", "run", "Config", "Server"]' 'class Config: pass' 'class Server: pass' 'def main(): pass' 'def run(): pass' > /workspace/uvicorn/__init__.py
cat > /workspace/setup.py <<'PY'
from setuptools import setup

setup(name="uvicorn", version="0.52.4", packages=["uvicorn"], entry_points={"console_scripts": ["uvicorn=uvicorn:main"]})
PY
