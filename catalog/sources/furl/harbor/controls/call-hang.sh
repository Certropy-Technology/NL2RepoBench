#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/furl
printf '%s\n' 'from .furl import furl' '__all__ = ["furl"]' > /workspace/furl/__init__.py
printf '%s\n' 'class furl:' '    def __init__(self, url=""):' '        while True: pass' > /workspace/furl/furl.py
printf '%s\n' 'from setuptools import setup' 'setup(name="furl", version="0.0.0", packages=["furl"])' > /workspace/setup.py
