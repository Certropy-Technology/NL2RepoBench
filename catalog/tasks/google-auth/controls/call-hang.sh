#!/usr/bin/env bash
# Control: the candidate installs cleanly but hangs when the adapter imports it.
# The verifier must kill the adapter and report a bounded timeout, not stall.
set -euo pipefail

mkdir -p /workspace/google/auth
cat > /workspace/setup.py <<'PY'
from setuptools import setup

setup(
    name="google-auth",
    version="2.56.3",
    packages=["google", "google.auth"],
)
PY
printf '' > /workspace/google/__init__.py
printf '' > /workspace/google/auth/__init__.py
printf 'while True:\n    pass\n' > /workspace/google/auth/_cache.py
