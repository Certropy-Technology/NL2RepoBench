#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
mkdir -p /workspace/websocket
printf '%s\n' 'while True: pass' > /workspace/websocket/__init__.py
printf '%s\n' 'from setuptools import setup' 'setup(name="websocket-client", version="1.9.0", packages=["websocket"])' > /workspace/setup.py
