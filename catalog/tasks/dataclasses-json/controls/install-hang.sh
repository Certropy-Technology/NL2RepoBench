#!/usr/bin/env bash
set -euo pipefail

cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = []
build-backend = "backend"
backend-path = ["."]

[project]
name = "dataclasses-json"
version = "0.0.0"
TOML
cat > /workspace/backend.py <<'PY'
import time

def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    time.sleep(600)
PY
