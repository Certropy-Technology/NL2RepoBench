#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/oauthlib
printf '__version__ = "3.4.0"\n' > /workspace/oauthlib/__init__.py
cat > /workspace/setup.py <<'PY'
from setuptools import setup
setup(name="oauthlib", version="3.4.0", packages=["oauthlib"])
PY
