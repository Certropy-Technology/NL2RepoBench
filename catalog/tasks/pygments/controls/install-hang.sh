#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
printf '%s\n' 'import time; time.sleep(600)' > /workspace/setup.py
