#!/usr/bin/env bash
set -euo pipefail
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["flit_core==3.12.0"]
build-backend = "flit_core.buildapi"
[project]
name = "pathspec"
version = "1.1.1"
description = "Installable low-behavior pathspec control"
TOML
mkdir -p /workspace/pathspec
cat > /workspace/pathspec/__init__.py <<'PY'
__version__ = "1.1.1"
PY
