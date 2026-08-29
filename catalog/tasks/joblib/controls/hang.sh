#!/usr/bin/env bash
set -euo pipefail

cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools==84.0.0"]
build-backend = "setuptools.build_meta"

[project]
name = "joblib"
version = "1.6.dev0"

[tool.setuptools]
packages = ["joblib"]
TOML

mkdir -p /workspace/joblib
cat > /workspace/joblib/__init__.py <<'PY'
import time
time.sleep(3600)
PY
