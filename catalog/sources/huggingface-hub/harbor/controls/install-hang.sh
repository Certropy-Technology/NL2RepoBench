#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = []
build-backend = "hang_backend"
backend-path = ["."]
[project]
name = "huggingface_hub"
version = "1.29.0.dev0"
TOML
cat > /workspace/hang_backend.py <<'PY'
import time

def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    time.sleep(600)

def prepare_metadata_for_build_wheel(metadata_directory, config_settings=None):
    time.sleep(600)
PY
