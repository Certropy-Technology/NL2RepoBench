#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
printf '%s\n' \
  '[build-system]' \
  'requires = []' \
  'build-backend = "hang_backend"' \
  'backend-path = ["."]' \
  > /workspace/pyproject.toml
printf '%s\n' \
  'import time' \
  'time.sleep(300)' \
  > /workspace/hang_backend.py
