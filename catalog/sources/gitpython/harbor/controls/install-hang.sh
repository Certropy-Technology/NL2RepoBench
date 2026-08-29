#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
printf '%s\n' 'from setuptools import setup; setup(name="GitPython", version="3.1.60")' > /workspace/setup.py
printf '%s\n' 'import time; time.sleep(600)' > /workspace/setup.py
