#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/httptools
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"
[project]
name = "httptools"
version = "0.8.0"
EOF
cat > /workspace/httptools/__init__.py <<'EOF'
import time

time.sleep(600)
EOF
