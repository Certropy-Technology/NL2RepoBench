#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
mkdir -p /workspace/src/hatchling
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[project]
name = "hatchling"
version = "1.32.0"
TOML
cat > /workspace/src/hatchling/__init__.py <<'PY'
while True:
    pass
PY
