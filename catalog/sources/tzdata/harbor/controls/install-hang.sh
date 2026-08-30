#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = []
build-backend = "hang_backend"
backend-path = ["."]

[project]
name = "tzdata"
version = "2026.3"
EOF
cat > /workspace/hang_backend.py <<'PY'
import time

def get_requires_for_build_wheel(config_settings=None):
    return []

def prepare_metadata_for_build_wheel(metadata_directory, config_settings=None):
    time.sleep(300)

def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    time.sleep(300)
PY
