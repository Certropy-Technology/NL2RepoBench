#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
printf '%s\n' 'import time' '' 'from setuptools import setup' '' 'time.sleep(3600)' '' 'setup(name="google-api-core", version="2.35.0")' > /workspace/setup.py
