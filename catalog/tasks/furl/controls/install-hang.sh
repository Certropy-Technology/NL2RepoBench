#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/furl
printf '%s\n' 'from setuptools import setup' 'setup(name="furl", version="0.0.0", packages=["furl"])' > /workspace/setup.py
printf '%s\n' 'while True: pass' > /workspace/furl/__init__.py
