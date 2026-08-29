#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/pathvalidate
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools==84.0.0"]
build-backend = "setuptools.build_meta"
[project]
name = "pathvalidate"
version = "3.3.1"
TOML
cat > /workspace/pathvalidate/__init__.py <<'PY'
import time
time.sleep(300)
PY
