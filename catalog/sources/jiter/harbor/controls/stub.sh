#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools==80.9.0"]
build-backend = "setuptools.build_meta"
[project]
name = "jiter"
version = "0.0.0"
EOF
mkdir -p /workspace/jiter
printf 'def from_json(*args, **kwargs): return None\n' > /workspace/jiter/__init__.py
