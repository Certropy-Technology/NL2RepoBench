#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/certifi
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools==80.10.2", "wheel==0.45.1"]
build-backend = "setuptools.build_meta"

[project]
name = "certifi"
version = "2026.07.22"

[tool.setuptools]
packages = ["certifi"]
TOML
cat > /workspace/certifi/__init__.py <<'PY'
import time
time.sleep(600)
PY
