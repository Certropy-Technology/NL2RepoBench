#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/Lib/fontTools
printf '%s\n' '__version__ = "4.63.1.dev0"' > /workspace/Lib/fontTools/__init__.py
cat > /workspace/setup.py <<'PY'
import time
while True:
    time.sleep(1)
PY
