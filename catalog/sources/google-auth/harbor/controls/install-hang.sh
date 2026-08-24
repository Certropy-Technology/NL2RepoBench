#!/usr/bin/env bash
# Control: the candidate build backend hangs. The verifier must kill the install
# at its bounded timeout and classify it as a candidate (model) failure.
set -euo pipefail

mkdir -p /workspace
cat > /workspace/setup.py <<'PY'
import time

from setuptools import setup

time.sleep(3600)
setup(name="google-auth", version="2.56.3")
PY
