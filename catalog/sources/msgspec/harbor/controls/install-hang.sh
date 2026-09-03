#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools==80.9.0", "setuptools-scm==8.3.1", "wheel==0.45.1"]
build-backend = "hang_backend"
backend-path = ["."]
[project]
name = "msgspec"
version = "0.1.0"
TOML
cat > /workspace/hang_backend.py <<'PY'
import time
time.sleep(600)
PY
