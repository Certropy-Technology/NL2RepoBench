#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/dataclasses_json
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[project]
name = "dataclasses-json"
version = "0.0.0"
TOML
cat > /workspace/dataclasses_json/__init__.py <<'PY'
import time
time.sleep(600)
PY
