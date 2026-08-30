#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/zipp/compat
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[project]
name = "zipp"
version = "4.1.0"
TOML
cat > /workspace/zipp/__init__.py <<'PY'
__all__ = ["Path"]

class Path:
    def __init__(self, root, at=""):
        self.root = root
        self.at = at
PY
touch /workspace/zipp/compat/__init__.py
