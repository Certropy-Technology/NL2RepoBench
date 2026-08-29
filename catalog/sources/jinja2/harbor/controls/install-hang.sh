#!/usr/bin/env bash
set -euo pipefail
cd /tmp
rm -rf /workspace
mkdir -p /workspace/jinja2
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["flit_core<4"]
build-backend = "hang_backend:build_wheel"
backend-path = ["."]
[project]
name = "Jinja2"
version = "3.2.0.dev"
description = "install timeout"
[tool.flit.module]
name = "jinja2"
TOML
cat > /workspace/hang_backend.py <<'PY'
import time
def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    time.sleep(600)
    return 'never.whl'
PY
