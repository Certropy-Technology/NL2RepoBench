#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
printf '%s\n' 'from setuptools import setup' 'setup(name="requests-cache",version="1.3.4")' > /workspace/setup.py
printf '%s\n' 'while True: pass' > /workspace/setup.py
