#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/distro
cat > /workspace/setup.py <<'PY'
from setuptools import setup
setup(name="distro", version="1.9.0", packages=["distro"])
PY
cat > /workspace/distro/__init__.py <<'PY'
import time
__version__ = "1.9.0"
def id():
    time.sleep(600)
PY
