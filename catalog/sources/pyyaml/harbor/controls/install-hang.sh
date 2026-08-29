#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools==84.0.0", "wheel==0.48.0"]
build-backend = "hang_backend"
backend-path = ["."]

[project]
name = "PyYAML"
version = "7.0.0.dev0"
TOML
cat > /workspace/hang_backend.py <<'PY'
import subprocess
import sys
import time

subprocess.Popen(
    [sys.executable, "-c", "import time; time.sleep(600)"],
    start_new_session=True,
)
time.sleep(600)
PY
