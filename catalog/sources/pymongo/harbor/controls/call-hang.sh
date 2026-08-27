#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/pymongo /workspace/bson
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools==80.9.0"]
build-backend = "setuptools.build_meta"

[project]
name = "pymongo"
version = "4.18.0.dev0"

[tool.setuptools]
packages = ["bson", "pymongo"]
TOML
cat > /workspace/pymongo/__init__.py <<'PY'
import time
time.sleep(600)
__version__ = "4.18.0.dev0"
PY
printf '' > /workspace/bson/__init__.py
