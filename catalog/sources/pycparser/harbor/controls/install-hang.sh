#!/usr/bin/env bash
set -euo pipefail
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools==80.9.0"]
build-backend = "build_backend"
backend-path = ["."]
[project]
name = "pycparser"
version = "3.00"
TOML
cat > /workspace/build_backend.py <<'PY'
import time
def get_requires_for_build_wheel(config_settings=None):
    time.sleep(600)
    return []
PY
