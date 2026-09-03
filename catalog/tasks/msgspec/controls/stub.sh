#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/msgspec
printf '%s\n' 'class Struct: pass' > /workspace/msgspec/__init__.py
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools==80.9.0", "setuptools-scm==8.3.1", "wheel==0.45.1"]
build-backend = "setuptools.build_meta"
[project]
name = "msgspec"
version = "0.1.0"
[tool.setuptools.packages.find]
where = ["."]
TOML
