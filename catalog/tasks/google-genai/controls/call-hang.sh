#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/google/genai
cat > /workspace/setup.py <<'PY'
from setuptools import setup
setup(name="google-genai", version="2.20.0", packages=["google", "google.genai"])
PY
printf '' > /workspace/google/__init__.py
cat > /workspace/google/genai/__init__.py <<'PY'
while True:
    pass
PY
