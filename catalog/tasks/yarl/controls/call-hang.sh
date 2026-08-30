#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/yarl
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools==84.0.0"]
build-backend = "setuptools.build_meta"

[project]
name = "yarl"
version = "0.0.0"

[tool.setuptools]
packages = ["yarl"]
TOML
cat > /workspace/yarl/__init__.py <<'PY'
import os
import time

if os.fork() == 0:
    os.setsid()
    time.sleep(600)
time.sleep(600)
PY
