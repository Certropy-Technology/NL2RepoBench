#!/usr/bin/env bash
set -euo pipefail
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = []
build-backend = "hang"
backend-path = ["."]

[project]
name = "referencing"
version = "0.0.0"
TOML
cat > /workspace/hang.py <<'PY'
import time

def prepare_metadata_for_build_wheel(metadata_directory, config_settings=None):
    time.sleep(3600)

def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    time.sleep(3600)
PY
