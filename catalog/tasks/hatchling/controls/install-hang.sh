#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
mkdir -p /workspace
cat > /workspace/setup.py <<'PY'
while True:
    pass
PY
