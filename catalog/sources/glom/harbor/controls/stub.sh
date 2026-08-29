#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/glom
cat > /workspace/setup.py <<'PY'
from setuptools import setup
setup(name="glom", version="0.0.0", packages=["glom"])
PY
cat > /workspace/glom/__init__.py <<'PY'
__version__ = "0.0.0"
PY
