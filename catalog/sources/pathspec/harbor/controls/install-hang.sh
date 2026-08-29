#!/usr/bin/env bash
set -euo pipefail
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools==75.8.0"]
build-backend = "setuptools.build_meta"
[project]
name = "pathspec"
version = "1.1.1"
TOML
cat > /workspace/setup.py <<'PY'
while True:
    pass
PY
