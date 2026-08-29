#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
[project]
name = "python-multipart"
version = "0.0.0"
EOF
cat > /workspace/setup.py <<'PY'
while True:
    pass
PY
