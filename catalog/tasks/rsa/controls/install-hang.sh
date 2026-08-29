#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/rsa
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = []
build-backend = "backend"
backend-path = ["."]
[project]
name = "rsa"
version = "4.10.dev0"
EOF
cat > /workspace/backend.py <<'EOF'
import time
def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    time.sleep(600)
EOF
printf '__version__ = "4.10-dev0"\n' > /workspace/rsa/__init__.py
