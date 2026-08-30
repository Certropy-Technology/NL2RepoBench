#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/hang_backend /workspace/yarl
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = []
build-backend = "hang_backend"
backend-path = ["."]
TOML
cat > /workspace/hang_backend/__init__.py <<'PY'
import os
import time

def get_requires_for_build_wheel(config_settings=None):
    if os.fork() == 0:
        os.setsid()
        time.sleep(600)
    time.sleep(600)

def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    time.sleep(600)
PY
printf '__version__ = "0.0.0"\n' > /workspace/yarl/__init__.py
