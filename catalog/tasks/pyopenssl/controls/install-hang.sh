#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' '[build-system]' 'requires = []' 'build-backend = "backend"' > /workspace/pyproject.toml
printf 'import time\ntime.sleep(600)\n' > /workspace/backend.py
