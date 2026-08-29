#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/langchain
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "langchain"
version = "0.0.0"
EOF
cat > /workspace/langchain/__init__.py <<'EOF'
__version__ = "0.0.0"
EOF
