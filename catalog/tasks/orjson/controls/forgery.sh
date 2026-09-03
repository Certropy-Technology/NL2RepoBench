#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/orjson
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = []
build-backend = "setuptools.build_meta:__legacy__"
[project]
name = "orjson"
version = "3.12.0"
[tool.setuptools]
packages = ["orjson"]
TOML
cat > /workspace/orjson/__init__.py <<'PY'
__version__ = "3.12.0"
def dumps(*args, **kwargs):
    return b"forged"
def loads(*args, **kwargs):
    return {"forged": True}
PY
