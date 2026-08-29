#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
mkdir -p /workspace
printf '%s\n' '[build-system]' 'build-backend = "backend"' > /workspace/pyproject.toml
printf '%s\n' 'import time' 'time.sleep(600)' > /workspace/backend.py
