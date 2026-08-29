#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cat > /workspace/setup.py <<'PY'
import time
time.sleep(1800)
PY
