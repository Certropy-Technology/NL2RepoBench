#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
mkdir -p /workspace
printf '%s\n' '[build-system]' 'requires = []' 'build-backend = "backend"' 'backend-path = ["."]' '' '[project]' 'name = "websocket-client"' 'version = "1.9.0"' > /workspace/pyproject.toml
printf '%s\n' 'import time' '' 'def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):' '    time.sleep(300)' '    return "never-built.whl"' '' 'def prepare_metadata_for_build_wheel(metadata_directory, config_settings=None):' '    time.sleep(300)' '    return "websocket_client-1.9.0.dist-info"' > /workspace/backend.py
