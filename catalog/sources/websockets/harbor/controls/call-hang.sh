#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/websockets
printf '%s\n' 'from setuptools import setup' 'setup(name="websockets", version="17.1", packages=["websockets"])' > /workspace/setup.py
printf '%s\n' 'import time' 'time.sleep(300)' > /workspace/websockets/__init__.py
