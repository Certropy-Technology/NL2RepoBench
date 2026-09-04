#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = []
build-backend = "backend"
backend-path = ["."]
[project]
name = "CacheControl"
version = "0.14.4"
EOF
cat > /workspace/backend.py <<'EOF'
import time

def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    time.sleep(300)
    return "never-built.whl"

def prepare_metadata_for_build_wheel(metadata_directory, config_settings=None):
    time.sleep(300)
    return "cachecontrol-0.14.4.dist-info"
EOF
