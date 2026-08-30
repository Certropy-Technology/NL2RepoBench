#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/websockets
printf '%s\n' 'from setuptools import setup' 'setup(name="websockets", version="17.1", packages=["websockets"])' > /workspace/setup.py
printf '%s\n' '__version__ = "17.1"' '__all__ = []' > /workspace/websockets/__init__.py
