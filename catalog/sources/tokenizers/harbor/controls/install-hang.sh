#!/usr/bin/env bash
set -euo pipefail
cat > /workspace/setup.py <<'PY'
import time
time.sleep(1000)
PY
