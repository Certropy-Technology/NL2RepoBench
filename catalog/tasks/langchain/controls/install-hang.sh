#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[project]
name = "langchain"
version = "0.0.0"
EOF
cat > /workspace/setup.py <<'EOF'
import time
time.sleep(300)
EOF
