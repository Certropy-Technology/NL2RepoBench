#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cat > /workspace/setup.py <<'PY'
import time

from setuptools import setup

time.sleep(600)
setup(name="python-discovery", version="0.0.0")
PY
