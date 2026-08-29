#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cat > /workspace/setup.py <<'PY'
import time

from setuptools import setup

time.sleep(3600)
setup(name="importlib_metadata", version="8.9.1.dev28")
PY
