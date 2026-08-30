#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/backend
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = []
build-backend = "backend"
backend-path = ["backend"]
[project]
name = "tomli"
version = "2.4.1"
requires-python = ">=3.8"
EOF
cat > /workspace/backend/backend.py <<'EOF'
import time

def get_requires_for_build_wheel(config_settings=None):
    return []

def prepare_metadata_for_build_wheel(metadata_directory, config_settings=None):
    time.sleep(600)

def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    time.sleep(600)
