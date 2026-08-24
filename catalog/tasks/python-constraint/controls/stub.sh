#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/constraint
cat > /workspace/pyproject.toml <<'PYPROJECT'
[build-system]
requires = ["poetry-core==2.4.1"]
build-backend = "poetry.core.masonry.api"
[project]
name = "python-constraint2"
version = "2.7.3"
requires-python = ">=3.11"
[tool.poetry]
packages = [{ include = "constraint" }]
PYPROJECT
cat > /workspace/constraint/__init__.py <<'PY'
class Problem:
    def __init__(self, *args, **kwargs): pass
PY
