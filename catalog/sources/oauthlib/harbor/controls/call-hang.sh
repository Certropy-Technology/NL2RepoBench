#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/oauthlib
cat > /workspace/setup.py <<'PY'
from setuptools import setup
setup(name="oauthlib", version="3.4.0", packages=["oauthlib"])
PY
cat > /workspace/oauthlib/__init__.py <<'PY'
import time
__version__ = "3.4.0"
def set_debug(value): pass
def get_debug(): return False
def quote(value): time.sleep(600)
PY
