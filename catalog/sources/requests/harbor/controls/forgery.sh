#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
mkdir -p /workspace
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"
[project]
name = "requests"
version = "2.32.5"
EOF
mkdir -p /workspace/requests
printf '__version__ = "2.32.5"\n' > /workspace/requests/__init__.py
