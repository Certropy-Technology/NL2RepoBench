#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/orjson
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools==80.9.0"]
build-backend = "setuptools.build_meta"
[project]
name = "orjson"
version = "3.12.0"
[tool.setuptools]
packages = ["orjson"]
TOML
cat > /workspace/orjson/__init__.py <<'PY'
while True:
    pass
PY
