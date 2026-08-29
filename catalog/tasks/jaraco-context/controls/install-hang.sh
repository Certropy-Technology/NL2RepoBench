#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/build
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = []
build-backend = "hang_backend"
backend-path = ["build"]
[project]
name = "jaraco.context"
version = "6.1.2"
EOF
cat > /workspace/build/hang_backend.py <<'PY'
import time
time.sleep(600)
PY
