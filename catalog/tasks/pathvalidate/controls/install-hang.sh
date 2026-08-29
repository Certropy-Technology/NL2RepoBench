#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = []
build-backend = "hang_backend"
backend-path = ["."]
[project]
name = "pathvalidate"
version = "3.3.1"
TOML
cat > /workspace/hang_backend.py <<'PY'
import time

def get_requires_for_build_wheel(config_settings=None):
    return []

def prepare_metadata_for_build_wheel(metadata_directory, config_settings=None):
    time.sleep(300)

def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    time.sleep(300)
PY
