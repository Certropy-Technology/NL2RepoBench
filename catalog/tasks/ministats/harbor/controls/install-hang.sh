#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace

cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools>=70", "wheel"]
build-backend = "hang_backend"
backend-path = ["."]

[project]
name = "ministats-bench"
version = "1.0.0"
dependencies = []
EOF

cat > /workspace/hang_backend.py <<'EOF'
import subprocess
import sys
import time

subprocess.Popen(
    [sys.executable, "-c", "import time; time.sleep(600)"],
    start_new_session=True,
)
time.sleep(600)
EOF
