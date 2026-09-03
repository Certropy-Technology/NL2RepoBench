#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/factory
cat > /workspace/factory/__init__.py <<'PY'
import time
time.sleep(600)
PY
cat > /workspace/setup.py <<'PY'
from setuptools import setup
setup(name="factory_boy", version="3.3.4.dev0", packages=["factory"])
PY
