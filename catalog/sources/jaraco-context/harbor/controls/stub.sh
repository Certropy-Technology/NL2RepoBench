#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/jaraco/context
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"
[project]
name = "jaraco.context"
version = "6.1.2"
EOF
printf '%s\n' '# intentionally incomplete' > /workspace/jaraco/context/__init__.py
