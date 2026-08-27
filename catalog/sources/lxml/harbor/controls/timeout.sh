#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/lxml
printf '%s\n' '__version__ = "0"' > /workspace/lxml/__init__.py
printf '%s\n' 'import time; time.sleep(60)' > /workspace/lxml/etree.py
printf '%s\n' 'from setuptools import setup; setup(name="lxml", version="0")' > /workspace/setup.py
