#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
printf '%s\n' 'import time; time.sleep(600)' > /workspace/setup.py
