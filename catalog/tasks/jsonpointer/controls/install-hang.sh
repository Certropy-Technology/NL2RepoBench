#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace
cat > /workspace/setup.py <<'PY'
import time

time.sleep(1000)
PY
cat > /workspace/jsonpointer.py <<'PY'
__version__ = "3.1.1"
PY
