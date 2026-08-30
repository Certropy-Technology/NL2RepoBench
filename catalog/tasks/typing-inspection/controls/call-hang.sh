#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/typing_inspection
cat > /workspace/typing_inspection/__init__.py <<'PY'
import time

time.sleep(600)
PY
cat > /workspace/setup.py <<'PY'
from setuptools import setup

setup(name="typing-inspection", version="0.4.4", packages=["typing_inspection"])
PY
