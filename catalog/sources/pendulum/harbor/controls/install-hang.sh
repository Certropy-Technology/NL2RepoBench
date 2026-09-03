#!/usr/bin/env bash
set -euo pipefail

cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = []
build-backend = "backend"
backend-path = ["."]
EOF
cat > /workspace/backend.py <<'EOF'
import time

def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    time.sleep(3600)
EOF
