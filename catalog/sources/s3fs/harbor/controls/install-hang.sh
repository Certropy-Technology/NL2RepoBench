#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/s3fs
cat > /workspace/setup.py <<'PY'
import time
time.sleep(240)
PY
