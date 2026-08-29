#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = []
build-backend = "hang_backend"
backend-path = ["."]
TOML
cat > /workspace/hang_backend.py <<'PY'
while True:
    pass
PY
