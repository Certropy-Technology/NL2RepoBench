#!/usr/bin/env bash
set -euo pipefail

cat > /workspace/setup.py <<'PY'
import time

time.sleep(600)
PY
