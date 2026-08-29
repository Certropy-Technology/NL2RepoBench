#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/gitdb
cat > /workspace/pyproject.toml <<'PYPROJECT'
[build-system]
requires = ["setuptools==80.9.0"]
build-backend = "setuptools.build_meta"
[project]
name = "gitdb"
version = "0.0.0"
requires-python = ">=3.9"
dependencies = ["smmap==5.0.3"]
PYPROJECT
cat > /workspace/gitdb/__init__.py <<'PY'
import time
time.sleep(600)
PY
