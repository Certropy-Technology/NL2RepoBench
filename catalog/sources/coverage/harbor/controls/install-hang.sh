#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/coverage
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools==84.0.0"]
build-backend = "setuptools.build_meta"

[project]
name = "coverage"
version = "7.16.0a0.dev1"

[tool.setuptools]
packages = ["coverage"]
TOML
cat > /workspace/setup.py <<'PY'
import time
time.sleep(180)
from setuptools import setup
setup(name="coverage", version="7.16.0a0.dev1", packages=["coverage"])
PY
cat > /workspace/coverage/__init__.py <<'PY'
raise RuntimeError('install should time out before import')
PY
