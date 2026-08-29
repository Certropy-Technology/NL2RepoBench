#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
mkdir -p /workspace/msal
printf '%s\n' "from setuptools import setup; setup(name='msal', version='1.38.0', packages=['msal'])" > /workspace/setup.py
printf '%s\n' 'import time; time.sleep(600)' > /workspace/msal/__init__.py
