#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
mkdir -p /workspace/python_multipart
printf '__version__ = "0.0.0"\n' > /workspace/python_multipart/__init__.py
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
[project]
name = "python-multipart"
version = "0.0.0"
EOF
