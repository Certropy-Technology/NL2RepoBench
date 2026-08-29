#!/usr/bin/env bash
set -euo pipefail
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = []
build-backend = "backend"
backend-path = ["."]
[project]
name = "propcache"
version = "0.0.0"
TOML
cat > /workspace/backend.py <<'PY'
import time

def build_wheel(*args, **kwargs):
    time.sleep(3600)

def get_requires_for_build_wheel(*args, **kwargs):
    return []
PY
