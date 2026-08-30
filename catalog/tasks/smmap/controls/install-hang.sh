#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
cat > /workspace/setup.py <<'PY'
import time

time.sleep(600)
PY
