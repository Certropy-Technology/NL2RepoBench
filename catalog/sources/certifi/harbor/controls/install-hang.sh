#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools==80.10.2", "wheel==0.45.1"]
build-backend = "backend"
backend-path = ["."]

[project]
name = "certifi"
version = "2026.07.22"
TOML
cat > /workspace/backend.py <<'PY'
import time
time.sleep(600)
PY
