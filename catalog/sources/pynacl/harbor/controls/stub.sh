#!/usr/bin/env bash
set -euo pipefail

cat > pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools==84.0.0"]
build-backend = "setuptools.build_meta"

[project]
name = "PyNaCl"
version = "1.6.2"
requires-python = ">=3.8"
EOF
mkdir -p nacl
cat > nacl/__init__.py <<'EOF'
__version__ = "1.6.2"
__all__ = []
EOF
