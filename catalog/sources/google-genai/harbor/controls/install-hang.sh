#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace
cat > /workspace/setup.py <<'PY'
import time
from setuptools import setup
time.sleep(3600)
setup(name="google-genai", version="2.20.0")
PY
