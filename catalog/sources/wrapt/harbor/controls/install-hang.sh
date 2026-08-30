#!/usr/bin/env bash
set -euo pipefail
cat > /workspace/setup.py <<'PY'
import time
time.sleep(120)
PY
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools==84.0.0"]
build-backend = "setuptools.build_meta"
[project]
name = "wrapt"
version = "2.4.0rc5"
TOML
