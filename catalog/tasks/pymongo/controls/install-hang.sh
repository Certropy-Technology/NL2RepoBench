#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = []
build-backend = "backend"
backend-path = ["."]
EOF
cat > /workspace/backend.py <<'EOF'
import time
time.sleep(600)
EOF
