#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/pendulum
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"
[project]
name = "pendulum"
version = "3.2.0"
EOF
cat > /workspace/pendulum/__init__.py <<'EOF'
import time

def __getattr__(name):
    def hang(*args, **kwargs):
        time.sleep(3600)
    return hang
EOF
