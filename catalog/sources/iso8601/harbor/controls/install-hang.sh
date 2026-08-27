#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace
mkdir -p /workspace
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = []
build-backend = "hang_backend"
backend-path = ["."]

[project]
name = "iso8601"
version = "2.1.0"
TOML
cat > /workspace/hang_backend.py <<'PY'
import subprocess
import sys
import time

subprocess.Popen([sys.executable, "-c", "import time; time.sleep(600)"], start_new_session=True)
time.sleep(600)
PY
