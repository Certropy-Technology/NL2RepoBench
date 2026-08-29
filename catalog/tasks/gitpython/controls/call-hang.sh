#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/git
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools==84.0.0"]
build-backend = "setuptools.build_meta"
[project]
name = "GitPython"
version = "3.1.60"
[tool.setuptools]
packages = ["git"]
TOML
cat > /workspace/git/__init__.py <<'PY'
while True:
    pass
PY
