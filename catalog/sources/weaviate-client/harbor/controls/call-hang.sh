#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/weaviate
cat > /workspace/setup.py <<'PY'
from setuptools import setup

setup(name="weaviate-client", version="4.23.1.dev26+g9f59a367f", packages=["weaviate"])
PY
cat > /workspace/weaviate/__init__.py <<'PY'
import time

time.sleep(600)
PY
