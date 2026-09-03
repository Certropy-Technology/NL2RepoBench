#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/arrow
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = []
build-backend = "backend"
backend-path = ["."]

[project]
name = "arrow-install-hang"
version = "0.0.0"
TOML
cat > /workspace/backend.py <<'PY'
import time
time.sleep(3600)
PY
