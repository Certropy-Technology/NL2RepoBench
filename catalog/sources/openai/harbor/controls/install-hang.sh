#!/usr/bin/env bash
set -eu

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = []
build-backend = "slow_backend"
backend-path = ["."]

[project]
name = "openai"
version = "3.3.1"
EOF
cat > /workspace/slow_backend.py <<'EOF'
import time

def build_editable(*args, **kwargs):
    time.sleep(300)
    return "never-built.whl"

def build_wheel(*args, **kwargs):
    time.sleep(300)
    return "never-built.whl"
EOF
