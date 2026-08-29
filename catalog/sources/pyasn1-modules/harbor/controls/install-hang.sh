#!/usr/bin/env bash
set -euo pipefail
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = []
build-backend = "backend"
backend-path = ["."]
[project]
name = "pyasn1-modules"
version = "0.4.2"
TOML
cat > /workspace/backend.py <<'PY'
import time

def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    del wheel_directory, config_settings, metadata_directory
    while True:
        time.sleep(60)
PY
