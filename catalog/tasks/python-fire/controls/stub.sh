#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/fire
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools>=70", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "fire"
version = "0.7.1"
description = "stub control"
requires-python = ">=3.7"

[tool.setuptools]
packages = ["fire"]
EOF
cat > /workspace/fire/__init__.py <<'EOF'
__version__ = "0.7.1"
__all__ = ["Fire"]
def Fire(*args, **kwargs):
    raise NotImplementedError
EOF
