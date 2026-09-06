#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
mkdir -p /workspace/joblib
cat > /workspace/setup.py <<'PY'
from setuptools import setup
setup(name="joblib", version="0.0.0", packages=["joblib"])
PY
cat > /workspace/joblib/__init__.py <<'PY'
import subprocess
subprocess.Popen(["sh", "-c", "sleep 120"], start_new_session=True,
                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
PY
