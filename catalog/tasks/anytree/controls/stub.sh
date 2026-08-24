#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/anytree
cat > /workspace/pyproject.toml <<'PYPROJECT'
[build-system]
requires = ["pdm-backend"]
build-backend = "pdm.backend"
[project]
name = "anytree"
version = "0.0.0"
requires-python = ">=3.9.2,<4.0"
[tool.pdm.build]
includes = ["anytree"]
PYPROJECT
cat > /workspace/anytree/__init__.py <<'PY'
class Node:
    def __init__(self, *args, **kwargs):
        self.name = args[0] if args else kwargs.get("name")
PY
