#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace
mkdir -p /workspace
printf '%s\n' '[build-system]' 'requires = []' 'build-backend = "hang_backend"' 'backend-path = ["."]' '[project]' 'name = "isodate"' 'version = "0.0.0"' > /workspace/pyproject.toml
printf '%s\n' 'import time' 'time.sleep(600)' > /workspace/hang_backend.py
