#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = []
build-backend = "backend"
backend-path = ["."]

[project]
name = "urllib3"
version = "2.7.1.dev42"
EOF
cat > /workspace/backend.py <<'EOF'
import time

def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    time.sleep(300)
    return "never-built.whl"

def prepare_metadata_for_build_wheel(metadata_directory, config_settings=None):
    time.sleep(300)
    return "urllib3-2.7.1.dev42.dist-info"
EOF
