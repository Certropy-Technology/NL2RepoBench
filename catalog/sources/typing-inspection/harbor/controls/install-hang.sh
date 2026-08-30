#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/typing_inspection
touch /workspace/typing_inspection/__init__.py
cat > /workspace/setup.py <<'PY'
from setuptools import setup
import time

time.sleep(600)
setup(name="typing-inspection", version="0.4.4", packages=["typing_inspection"])
PY
