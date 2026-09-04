#!/usr/bin/env bash
set -euo pipefail

rm -rf /workspace/*
mkdir -p /workspace/annotated_types
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "annotated-types"
version = "0.0.0"
EOF
cat > /workspace/annotated_types/__init__.py <<'EOF'
__version__ = "0.0.0"
EOF
