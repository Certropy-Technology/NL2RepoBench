#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
mkdir -p /workspace/requests_oauthlib
cat > /workspace/setup.py <<'PY'
from setuptools import setup
setup(name="requests-oauthlib", version="0.0.0", packages=["requests_oauthlib"])
PY
cat > /workspace/requests_oauthlib/__init__.py <<'PY'
__version__ = "0.0.0"
PY
